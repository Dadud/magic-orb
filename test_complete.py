"""Stage C canonical validation: combined display + WiFi HTTP."""
from machine import Pin, UART
import sys
import time

from hardware_profile import (
    ESP_RX,
    ESP_TX,
    ESP_UART_BAUDRATE,
    ESP_UART_ID,
)

sys.path.append('/lib')
from st77916 import ST77916

# ============================================================
# CONFIG - Edit these before running Stage C
# ============================================================
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"
HTTP_HOST = "neverssl.com"
HTTP_PATH = "/"

print("🔮 Magic Orb - Stage C (Display + WiFi HTTP)")
print("=" * 49)
print("Canonical script: test_complete.py")
print("Prerequisite: Stage A and Stage B must PASS before Stage C.")
print("Failure signature (UART): no AT response")
print("Failure signature (Display): display init timeout")
print("Failure signature (HTTP): HTTP status parse fail")

print("\n[Stage C] Initializing display...")
start_ms = time.ticks_ms()
display = ST77916()
elapsed_ms = time.ticks_diff(time.ticks_ms(), start_ms)
if elapsed_ms > 5000:
    raise RuntimeError(f"display init timeout: {elapsed_ms}ms")

print(f"✓ Display initialized in {elapsed_ms}ms")
display.fill(display.BLACK)
display.text("Magic Orb", 130, 140, display.CYAN)
display.text("Stage C running", 110, 170, display.WHITE)
display.show()

uart = UART(ESP_UART_ID, baudrate=ESP_UART_BAUDRATE, tx=Pin(ESP_TX), rx=Pin(ESP_RX))


def at_cmd(cmd, timeout_ms=2000):
    while uart.any():
        uart.read()
    uart.write((cmd + "\r\n").encode())
    time.sleep_ms(timeout_ms)
    response = b""
    while uart.any():
        response += uart.read()
    return response.decode("utf-8", errors="ignore")


print("\n[Stage C] Probing AT channel...")
resp = at_cmd("AT", 600)
if "OK" not in resp:
    raise RuntimeError(f"no AT response: {resp[:120] if resp else 'empty'}")
print("✓ ESP-AT responded")

print("\n[Stage C] Connecting WiFi...")
if "OK" not in at_cmd("AT+CWMODE=1", 1000):
    raise RuntimeError("no AT response while setting station mode")
resp = at_cmd(f'AT+CWJAP="{WIFI_SSID}","{WIFI_PASS}"', 15000)
if "OK" not in resp and "WIFI GOT IP" not in resp:
    raise RuntimeError(f"wifi join fail: {resp[:160] if resp else 'empty'}")
print("✓ WiFi joined")

print("\n[Stage C] Running HTTP GET over TCP...")
if "OK" not in at_cmd("AT+CIPMUX=0", 800):
    raise RuntimeError("tcp setup fail: CIPMUX")
resp = at_cmd(f'AT+CIPSTART="TCP","{HTTP_HOST}",80', 7000)
if "OK" not in resp and "CONNECT" not in resp:
    raise RuntimeError(f"tcp connect fail: {resp[:160] if resp else 'empty'}")

request = (
    f"GET {HTTP_PATH} HTTP/1.1\r\n"
    f"Host: {HTTP_HOST}\r\n"
    "Connection: close\r\n"
    "\r\n"
)
resp = at_cmd(f"AT+CIPSEND={len(request)}", 2000)
if ">" not in resp and "OK" not in resp:
    raise RuntimeError(f"send prompt fail: {resp[:160] if resp else 'empty'}")

uart.write(request.encode())
time.sleep_ms(3500)
raw = b""
while uart.any():
    raw += uart.read()
http_blob = raw.decode("utf-8", errors="ignore")

status_code = None
for line in http_blob.split("\r\n"):
    if line.startswith("HTTP/1.1") or line.startswith("HTTP/1.0"):
        parts = line.split(" ")
        if len(parts) >= 2 and parts[1].isdigit():
            status_code = int(parts[1])
        break

if status_code is None:
    raise RuntimeError(f"HTTP status parse fail: {http_blob[:200] if http_blob else 'empty'}")

print(f"✓ HTTP status parsed: {status_code}")
at_cmd("AT+CIPCLOSE", 800)

display.fill(display.BLACK)
display.text("Stage C PASS", 120, 160, display.GREEN)
display.text(f"HTTP {status_code}", 130, 190, display.WHITE)
display.show()

print("\n✓ Stage C PASS")
