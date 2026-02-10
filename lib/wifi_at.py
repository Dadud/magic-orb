# EXPERIMENTAL (NON-TARGET RUNTIME): CircuitPython ESP-AT driver kept for reference only.
# ESP-AT WiFi driver for RP2350 + ESP32-WROOM
import busio
import time

class ESPATWiFi:
    """Wrapper for ESP32 running ESP-AT firmware over UART."""
    
    def __init__(self, uart_tx, uart_rx, baudrate=115200, debug=False):
        self.uart = busio.UART(uart_tx, uart_rx, baudrate=baudrate, timeout=1)
        self.debug = debug
        self._connected = False
        
    def _send_cmd(self, cmd: str, timeout: float = 2.0) -> tuple[bool, str]:
        """Send AT command and wait for response."""
        self.uart.reset_input_buffer()
        self.uart.write((cmd + "\r\n").encode())
        
        deadline = time.monotonic() + timeout
        response = b""
        
        while time.monotonic() < deadline:
            if self.uart.in_waiting:
                response += self.uart.read(self.uart.in_waiting)
                if b"OK\r\n" in response or b"ERROR\r\n" in response:
                    break
            time.sleep(0.01)
        
        text = response.decode("utf-8", errors="ignore")
        success = "OK" in text and "ERROR" not in text
        
        if self.debug:
            print(f"[AT] {cmd} -> {'OK' if success else 'FAIL'}")
            if not success:
                print(f"  Response: {text}")
        
        return success, text
    
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
        return ok and "STATUS:2" in resp or "STATUS:3" in resp
    
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
        
        return 0, text
