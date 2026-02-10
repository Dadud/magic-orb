# MAGIC ORB - ALL-IN-ONE TEST
# Copy this entire file, paste into Thonny or save as main.py

# ============================================================
# CONFIG - Edit these!
# ============================================================
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"

# Which UART pins for ESP32? (ESP TX -> RP2350 RX)
UART_TX_PIN = 0  # GP0
UART_RX_PIN = 1  # GP1

# ============================================================
# CODE - Don't edit below unless you know what you're doing
# ============================================================

from machine import UART, Pin
import time

print("\n🔮 Magic Orb Test")
print("=" * 40)

# Test ESP32 UART
print("\n📡 Testing ESP32 UART...")
uart = UART(0, baudrate=115200, tx=Pin(UART_TX_PIN), rx=Pin(UART_RX_PIN))

def at_cmd(cmd, timeout_ms=2000):
    """Send AT command, return response"""
    uart.write((cmd + "\r\n").encode())
    time.sleep_ms(timeout_ms)
    response = b""
    while uart.any():
        response += uart.read()
    return response.decode('utf-8', errors='ignore')

# Test AT
resp = at_cmd("AT", 500)
if "OK" in resp:
    print("  ✓ ESP32 responding to AT commands")
else:
    print(f"  ✗ No response: {resp[:100] if resp else 'empty'}")
    print("  Check wiring: ESP TX -> GP{UART_RX_PIN}, ESP RX -> GP{UART_TX_PIN}")

# Test WiFi
if "OK" in resp:
    print(f"\n📶 Connecting to {WIFI_SSID}...")

    # Set station mode
    at_cmd("AT+CWMODE=1", 500)

    # Connect
    resp = at_cmd(f'AT+CWJAP="{WIFI_SSID}","{WIFI_PASS}"', 15000)

    if "OK" in resp or "WIFI GOT IP" in resp:
        print("  ✓ WiFi connected!")

        # Get IP
        resp = at_cmd("AT+CIFSR", 1000)
        if "APIP" in resp or "STAIP" in resp:
            # Extract IP from response
            for line in resp.split('\n'):
                if 'STAIP' in line:
                    print(f"  IP: {line}")
    else:
        print(f"  ✗ WiFi failed: {resp[:200]}")

# Test Display (very basic - may need adjustment)
print("\n🖥️  Testing display...")
try:
    # Try importing common display libraries
    try:
        import st7789
        print("  Found st7789 driver")
    except:
        try:
            import gc9a01
            print("  Found gc9a01 driver")
        except:
            print("  No display driver found - need to check Waveshare examples")
            print("  Visit: https://github.com/waveshareteam/Pico_MircoPython_Examples")

except Exception as e:
    print(f"  Display check error: {e}")

print("\n" + "=" * 40)
print("Test complete!")
print("\nNext: Check Waveshare examples for display init code")
