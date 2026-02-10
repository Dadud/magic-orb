# MAGIC ORB - COMPLETE HARDWARE TEST
# Tests: Display + WiFi (ESP-AT) + Basic UI
from machine import Pin, UART
import time
import sys

from hardware_profile import (
    BACKUP_DISPLAY_DRIVER,
    BACKUP_DISPLAY_DRIVER_STATUS,
    BOARD_NAME,
    DISPLAY_BUS_TYPE,
    DISPLAY_CONTROLLER,
    DISPLAY_DRIVER,
    DISPLAY_DRIVER_STATUS,
    ESP_RX,
    ESP_TX,
    ESP_UART_BAUDRATE,
    ESP_UART_ID,
)

sys.path.append('/lib')
from st77916 import ST77916

print("\n🔮 Magic Orb - Complete Hardware Test")
print("=" * 40)
print(f"Board profile: {BOARD_NAME}")
print(f"Primary display driver: {DISPLAY_DRIVER} ({DISPLAY_DRIVER_STATUS})")
print(f"Backup display driver: {BACKUP_DISPLAY_DRIVER} ({BACKUP_DISPLAY_DRIVER_STATUS})")
print(f"Display bus/controller: {DISPLAY_BUS_TYPE} / {DISPLAY_CONTROLLER}")

# ============================================================
# CONFIG - Edit these!
# ============================================================
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"

# ============================================================
# TEST 1: Display
# ============================================================
print("\n📺 TEST 1: Display...")

try:
    display = ST77916()

    print("  ✓ Display initialized")

    # Show startup screen
    display.fill(display.BLACK)
    display.text("Magic Orb", 130, 160, display.CYAN)
    display.text("Testing...", 140, 190, display.WHITE)
    display.show()
    time.sleep(1)

    for color, name in [(display.RED, "RED"), (display.BLUE, "BLUE"), (display.GREEN, "GREEN")]:
        display.fill(color)
        display.show()
        time.sleep(0.3)

    display.fill(display.BLACK)
    display.show()

    display_ok = True

except Exception as e:
    print(f"  ✗ Display failed: {e}")
    print("  Check hardware_profile.py and display wiring/profile")
    display_ok = False
    display = None

# ============================================================
# TEST 2: WiFi (ESP-AT)
# ============================================================
print("\n📶 TEST 2: WiFi (ESP-AT)...")

try:
    uart = UART(ESP_UART_ID, baudrate=ESP_UART_BAUDRATE, tx=Pin(ESP_TX), rx=Pin(ESP_RX))

    def at_cmd(cmd, timeout_ms=2000):
        uart.write((cmd + "\r\n").encode())
        time.sleep_ms(timeout_ms)
        response = b""
        while uart.any():
            response += uart.read()
        return response.decode('utf-8', errors='ignore')

    resp = at_cmd("AT", 500)
    if "OK" in resp:
        print("  ✓ ESP32 responding")
        at_cmd("AT+CWMODE=1", 500)
        print(f"  Connecting to {WIFI_SSID}...")
        resp = at_cmd(f'AT+CWJAP="{WIFI_SSID}","{WIFI_PASS}"', 15000)

        if "OK" in resp or "WIFI GOT IP" in resp:
            print("  ✓ WiFi connected!")
            resp = at_cmd("AT+CIFSR", 1000)
            if "STAIP" in resp:
                for line in resp.split('\n'):
                    if 'STAIP' in line:
                        print(f"  {line.strip()}")
            wifi_ok = True
        else:
            print(f"  ✗ WiFi failed: {resp[:100]}")
            wifi_ok = False
    else:
        print(f"  ✗ ESP32 not responding: {resp[:50] if resp else 'empty'}")
        print(f"  Check wiring: ESP TX -> GP{ESP_RX}, ESP RX -> GP{ESP_TX}")
        wifi_ok = False

except Exception as e:
    print(f"  ✗ WiFi test failed: {e}")
    wifi_ok = False

print("\n" + "=" * 40)
print("TEST RESULTS:")
print(f"  Display: {'✓ PASS' if display_ok else '✗ FAIL'}")
print(f"  WiFi:    {'✓ PASS' if wifi_ok else '✗ FAIL'}")

if display_ok and display:
    display.fill(display.BLACK)
    display.text("Test Results", 130, 140, display.CYAN)
    display.text(f"Display: {'OK' if display_ok else 'FAIL'}", 130, 170, display.WHITE)
    display.text(f"WiFi: {'OK' if wifi_ok else 'FAIL'}", 130, 190, display.WHITE)
    display.show()

print("\n" + "=" * 40)

if display_ok and wifi_ok:
    print("✓ All tests passed!")
    print("\nNext steps:")
    print("1. Create secrets.py with WiFi + gateway config")
    print("2. Run code.py for PTT functionality")
else:
    print("✗ Some tests failed")
    print("\nTroubleshooting:")
    if not display_ok:
        print("- Confirm display controller/bus are ST77916/QSPI")
        print("- Check hardware_profile.py + QSPI pin mapping")
    if not wifi_ok:
        print("- Check ESP32 UART wiring")
        print("- Verify ESP32 has ESP-AT firmware")

print("\nDone!")
