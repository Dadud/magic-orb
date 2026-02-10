"""Stage B canonical validation: ESP-AT UART-only path."""
from machine import Pin, UART
import time

from hardware_profile import ESP_RX, ESP_TX, ESP_UART_BAUDRATE, ESP_UART_ID

print("🔮 Magic Orb - Stage B (ESP-AT UART-Only)")
print("=" * 47)
print("Canonical script: test_esp_at_uart.py")
print("Prerequisite: Stage A must already PASS before this stage.")
print("Failure signature if UART probe fails: no AT response")

uart = UART(ESP_UART_ID, baudrate=ESP_UART_BAUDRATE, tx=Pin(ESP_TX), rx=Pin(ESP_RX))


def at_cmd(cmd, timeout_ms=1200):
    while uart.any():
        uart.read()
    uart.write((cmd + "\r\n").encode())
    time.sleep_ms(timeout_ms)
    response = b""
    while uart.any():
        response += uart.read()
    return response.decode("utf-8", errors="ignore")


print("\n[Stage B] Probing AT channel...")
resp = at_cmd("AT", 600)
if "OK" not in resp:
    raise RuntimeError(f"no AT response: {resp[:120] if resp else 'empty'}")
print("✓ ESP-AT responded to AT")

print("\n[Stage B] Querying firmware...")
resp = at_cmd("AT+GMR", 1000)
if "OK" not in resp:
    raise RuntimeError(f"firmware query failed: {resp[:120] if resp else 'empty'}")
print("✓ Firmware query returned OK")

print("\n[Stage B] Verifying station mode set...")
resp = at_cmd("AT+CWMODE=1", 1000)
if "OK" not in resp:
    raise RuntimeError(f"station mode set failed: {resp[:120] if resp else 'empty'}")
print("✓ Station mode configured")

print("\n✓ Stage B PASS")
print("Proceed to Stage C only after Stage A + Stage B both PASS.")
