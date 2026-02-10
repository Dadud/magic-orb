# MAGIC ORB - COMPLETE HARDWARE TEST
# Tests: Display + WiFi (ESP-AT) + Basic UI
from machine import Pin, SPI, UART
import time
import sys

print("\n🔮 Magic Orb - Complete Hardware Test")
print("=" * 40)

# ============================================================
# CONFIG - Edit these!
# ============================================================
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"

# Display pins (adjust if needed)
LCD_DC   = 8
LCD_CS   = 9
LCD_SCK  = 10
LCD_MOSI = 11
LCD_MISO = 12
LCD_BL   = 13
LCD_RST  = 15

# ESP32 UART pins (adjust if needed)
ESP_TX   = 0  # GP0 -> ESP32 RX
ESP_RX   = 1  # GP1 <- ESP32 TX

# ============================================================
# TEST 1: Display
# ============================================================
print("\n📺 TEST 1: Display...")

try:
    sys.path.append('/lib')
    from gc9a01 import GC9A01

    spi = SPI(1, 60000000, sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))
    display = GC9A01(
        spi=spi,
        dc=Pin(LCD_DC, Pin.OUT),
        cs=Pin(LCD_CS, Pin.OUT),
        rst=Pin(LCD_RST, Pin.OUT),
        bl=Pin(LCD_BL, Pin.OUT)
    )

    print("  ✓ Display initialized")

    # Show startup screen
    display.fill(display.BLACK)
    display.text("Magic Orb", 130, 160, display.CYAN)
    display.text("Testing...", 140, 190, display.WHITE)
    display.show()
    time.sleep(1)

    # Flash colors
    for color, name in [(display.RED, "RED"), (display.BLUE, "BLUE"), (display.GREEN, "GREEN")]:
        display.fill(color)
        display.show()
        time.sleep(0.3)

    # Back to black
    display.fill(display.BLACK)
    display.show()

    display_ok = True

except Exception as e:
    print(f"  ✗ Display failed: {e}")
    print("  Check pin configuration in CONFIG section")
    display_ok = False
    display = None

# ============================================================
# TEST 2: WiFi (ESP-AT)
# ============================================================
print("\n📶 TEST 2: WiFi (ESP-AT)...")

try:
    uart = UART(0, baudrate=115200, tx=Pin(ESP_TX), rx=Pin(ESP_RX))

    def at_cmd(cmd, timeout_ms=2000):
        uart.write((cmd + "\r\n").encode())
        time.sleep_ms(timeout_ms)
        response = b""
        while uart.any():
            response += uart.read()
        return response.decode('utf-8', errors='ignore')

    # Test AT
    resp = at_cmd("AT", 500)
    if "OK" in resp:
        print("  ✓ ESP32 responding")

        # Set station mode
        at_cmd("AT+CWMODE=1", 500)

        # Connect to WiFi
        print(f"  Connecting to {WIFI_SSID}...")
        resp = at_cmd(f'AT+CWJAP="{WIFI_SSID}","{WIFI_PASS}"', 15000)

        if "OK" in resp or "WIFI GOT IP" in resp:
            print("  ✓ WiFi connected!")

            # Get IP
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
        print("  Check wiring: ESP TX -> GP{ESP_RX}, ESP RX -> GP{ESP_TX}")
        wifi_ok = False

except Exception as e:
    print(f"  ✗ WiFi test failed: {e}")
    wifi_ok = False

# ============================================================
# RESULTS
# ============================================================
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
        print("- Check LCD pin connections")
        print("- Try adjusting LCD_DC, LCD_CS, etc. in CONFIG")
    if not wifi_ok:
        print("- Check ESP32 UART wiring")
        print("- Verify ESP32 has ESP-AT firmware")

print("\nDone!")
