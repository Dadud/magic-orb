# EXPERIMENTAL (NON-TARGET RUNTIME): CircuitPython ESP-AT driver kept for reference only.
# ESP-AT WiFi driver for RP2350 + ESP32-WROOM
import busio
import time

class ESPATWiFi:
    """Wrapper for ESP32 running ESP-AT firmware over UART."""
    
    def __init__(self, uart_tx, uart_rx, baudrate=115200, debug="errors"):
        self.uart = busio.UART(uart_tx, uart_rx, baudrate=baudrate, timeout=1)
        self.debug = self._normalize_debug_level(debug)
        self._connected = False

    @staticmethod
    def _normalize_debug_level(debug) -> str:
        if isinstance(debug, bool):
            return "verbose" if debug else "silent"
        if debug in ("silent", "errors", "verbose"):
            return debug
        return "errors"

    def _log(self, level: str, message: str):
        thresholds = {"silent": 0, "errors": 1, "verbose": 2}
        if thresholds.get(self.debug, 1) >= thresholds[level]:
            print(message)

    @staticmethod
    def parse_response(response_text: str, command: str = None) -> dict:
        """Parse a raw AT response into echo/intermediate/status/payload sections."""
        lines = [line for line in response_text.replace("\r\n", "\n").split("\n") if line]
        echo = None
        status = None
        status_index = None

        if command:
            for idx, line in enumerate(lines):
                if line.strip() == command.strip():
                    echo = line
                    break

        for idx in range(len(lines) - 1, -1, -1):
            line = lines[idx].strip()
            if line in ("OK", "ERROR"):
                status = line
                status_index = idx
                break

        intermediate = []
        for idx, line in enumerate(lines):
            if echo is not None and line == echo:
                echo = None
                continue
            if status_index is not None and idx == status_index:
                continue
            intermediate.append(line)

        payload = ESPATWiFi._extract_payload(response_text)
        return {
            "echo": command if command and command in response_text else None,
            "intermediate": intermediate,
            "status": status,
            "payload": payload,
            "raw": response_text,
        }

    @staticmethod
    def _extract_payload(response_text: str) -> str:
        if "+IPD," in response_text:
            payloads = []
            cursor = 0
            while True:
                start = response_text.find("+IPD,", cursor)
                if start < 0:
                    break
                colon = response_text.find(":", start)
                if colon < 0:
                    break
                header = response_text[start + 5:colon]
                length_part = header.split(",")[-1].strip()
                payload_start = colon + 1
                try:
                    payload_len = int(length_part)
                    payloads.append(response_text[payload_start:payload_start + payload_len])
                    cursor = payload_start + payload_len
                except ValueError:
                    next_line = response_text.find("\r\n", payload_start)
                    if next_line < 0:
                        payloads.append(response_text[payload_start:])
                        break
                    payloads.append(response_text[payload_start:next_line])
                    cursor = next_line + 2
            return "".join(payloads)

        if "\r\n\r\n" in response_text and "HTTP/" in response_text:
            return response_text.split("\r\n\r\n", 1)[1]
        return ""

    @staticmethod
    def _is_retryable(cmd: str) -> bool:
        retryable = ("AT", "AT+CWMODE", "AT+CWJAP", "AT+CIPSTART", "AT+CIPSEND")
        return any(cmd.startswith(prefix) for prefix in retryable)
        
    def _send_cmd(self, cmd: str, timeout: float = 2.0, max_attempts: int = None) -> tuple[bool, str]:
        """Send AT command and wait for response."""
        attempts = max_attempts
        if attempts is None:
            attempts = 3 if self._is_retryable(cmd) else 1

        final_text = ""
        for attempt in range(1, attempts + 1):
            self.uart.reset_input_buffer()
            self.uart.write((cmd + "\r\n").encode())

            deadline = time.monotonic() + timeout
            response = b""

            while time.monotonic() < deadline:
                if self.uart.in_waiting:
                    response += self.uart.read(self.uart.in_waiting)
                    if b"\r\nOK\r\n" in response or b"\r\nERROR\r\n" in response:
                        break
                time.sleep(0.01)

            final_text = response.decode("utf-8", errors="ignore")
            parsed = self.parse_response(final_text, command=cmd)
            success = parsed["status"] == "OK"
            if success:
                self._log("verbose", f"[AT] {cmd} -> OK")
                return True, final_text

            self._log("errors", f"[AT] {cmd} attempt {attempt}/{attempts} failed")
            self._log("verbose", f"  Response: {final_text}")
            if attempt < attempts:
                backoff = min(0.8, 0.15 * (2 ** (attempt - 1)))
                time.sleep(backoff)

        return False, final_text

    def _close_socket(self):
        ok, _ = self._send_cmd("AT+CIPCLOSE", timeout=2.0, max_attempts=1)
        if not ok:
            self._log("errors", "[AT] AT+CIPCLOSE failed during cleanup")
    
    def connect(self, ssid: str, password: str) -> bool:
        """Connect to WiFi network."""
        # Test AT
        ok, _ = self._send_cmd("AT")
        if not ok:
            return False
        
        # Set station mode
        ok, _ = self._send_cmd("AT+CWMODE=1")
        if not ok:
            return False
        
        # Connect to AP
        ok, resp = self._send_cmd(f'AT+CWJAP="{ssid}","{password}"', timeout=15)
        self._connected = ok
        return ok
    
    def is_connected(self) -> bool:
        """Check if WiFi is connected."""
        ok, resp = self._send_cmd("AT+CIPSTATUS?")
        if not ok:
            return False
        parsed = self.parse_response(resp, command="AT+CIPSTATUS?")
        for line in parsed["intermediate"]:
            if line.startswith("STATUS:"):
                try:
                    code = int(line.split(":", 1)[1])
                    return code in (2, 3)
                except (ValueError, IndexError):
                    continue
        return False
    
    def http_get(self, url: str, headers: dict = None) -> tuple[int, str]:
        """Perform HTTP GET request. Returns (status_code, body)."""
        # Parse URL
        if url.startswith("http://"):
            url = url[7:]
        elif url.startswith("https://"):
            url = url[8:]
        
        if "/" in url:
            host, path = url.split("/", 1)
            path = "/" + path
        else:
            host = url
            path = "/"
        
        port = 80
        
        # Start TCP connection
        ok, _ = self._send_cmd(f'AT+CIPSTART="TCP","{host}",{port}', timeout=5)
        if not ok:
            return 0, "Connection failed"
        
        # Build request
        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "Connection: close\r\n"
        if headers:
            for k, v in headers.items():
                request += f"{k}: {v}\r\n"
        request += "\r\n"
        
        # Send request
        req_len = len(request)
        ok, _ = self._send_cmd(f"AT+CIPSEND={req_len}")
        if not ok:
            self._close_socket()
            return 0, "Send failed"
        
        time.sleep(0.1)
        self.uart.write(request.encode())
        
        # Read response
        deadline = time.monotonic() + 10
        response = b""
        
        while time.monotonic() < deadline:
            if self.uart.in_waiting:
                response += self.uart.read(self.uart.in_waiting)
                if b"+IPD," in response and b"CLOSED" in response:
                    break
            time.sleep(0.05)

        if not response:
            self._close_socket()
            return 0, "HTTP timeout"
        
        # Parse response
        text = response.decode("utf-8", errors="ignore")
        
        # Find body (after \r\n\r\n)
        if "\r\n\r\n" in text:
            header, body = text.split("\r\n\r\n", 1)
            # Extract status code
            if "HTTP/1.1" in header:
                status_line = header.split("\r\n")[0]
                parts = status_line.split()
                if len(parts) >= 2:
                    try:
                        status = int(parts[1])
                        return status, body
                    except:
                        pass

        self._close_socket()
        return 0, text
    
    def http_post(self, url: str, data: bytes, content_type: str = "application/octet-stream", headers: dict = None) -> tuple[int, str]:
        """Perform HTTP POST request. Returns (status_code, body)."""
        # Parse URL
        if url.startswith("http://"):
            url = url[7:]
        elif url.startswith("https://"):
            url = url[8:]
        
        if "/" in url:
            host, path = url.split("/", 1)
            path = "/" + path
        else:
            host = url
            path = "/"
        
        port = 80
        data_len = len(data)
        
        # Start TCP connection
        ok, _ = self._send_cmd(f'AT+CIPSTART="TCP","{host}",{port}', timeout=5)
        if not ok:
            return 0, "Connection failed"
        
        # Build request
        request = f"POST {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += f"Content-Type: {content_type}\r\n"
        request += f"Content-Length: {data_len}\r\n"
        request += "Connection: close\r\n"
        if headers:
            for k, v in headers.items():
                request += f"{k}: {v}\r\n"
        request += "\r\n"
        
        # Send headers first
        req_bytes = request.encode() + data
        req_len = len(req_bytes)
        
        ok, _ = self._send_cmd(f"AT+CIPSEND={req_len}")
        if not ok:
            self._close_socket()
            return 0, "Send failed"
        
        time.sleep(0.1)
        self.uart.write(req_bytes)
        
        # Read response
        deadline = time.monotonic() + 15
        response = b""
        
        while time.monotonic() < deadline:
            if self.uart.in_waiting:
                response += self.uart.read(self.uart.in_waiting)
                if b"+IPD," in response and b"CLOSED" in response:
                    break
            time.sleep(0.05)

        if not response:
            self._close_socket()
            return 0, "HTTP timeout"
        
        # Parse response
        text = response.decode("utf-8", errors="ignore")
        
        if "\r\n\r\n" in text:
            header, body = text.split("\r\n\r\n", 1)
            if "HTTP/1.1" in header:
                status_line = header.split("\r\n")[0]
                parts = status_line.split()
                if len(parts) >= 2:
                    try:
                        status = int(parts[1])
                        return status, body
                    except:
                        pass

        self._close_socket()
        return 0, text
