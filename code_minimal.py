# EXPERIMENTAL (NON-TARGET RUNTIME): CircuitPython hardware test kept for reference only.
#!/usr/bin/env python3
"""
Magic Orb - RP2350 Voice Node - MINIMAL START
Just WiFi + Display test to verify hardware works
"""
import board
import time
import busio
import digitalio
from lib.wifi_at import ESPATWiFi

# Import secrets
try:
    from secrets import SECRETS
except ImportError:
    print("ERROR: Create secrets.py from secrets.py.example!")
    while True:
        pass

print("=== Magic Orb Hardware Test ===\n")

# Test 1: WiFi via ESP-AT
print("Testing WiFi (ESP-AT)...")
# Adjust pins based on your ESP32 UART wiring
# ESP32 TX -> RP2350 GP1 (UART RX)
# ESP32 RX -> RP2350 GP0 (UART TX)
wifi = ESPATWiFi(board.GP0, board.GP1, debug=True)

if wifi.connect(SECRETS['wifi_ssid'], SECRETS['wifi_password']):
    print("✓ WiFi connected!")
    
    # Test HTTP
    print("\nTesting HTTP GET...")
    status, body = wifi.http_get("http://httpbin.org/get")
    print(f"Status: {status}")
    if status == 200:
        print("✓ HTTP works!")
    else:
        print(f"✗ HTTP failed: {body[:200]}")
else:
    print("✗ WiFi failed")

# Test 2: Display
print("\nTesting Display...")
try:
    import displayio
    from adafruit_display_text import label
    import terminalio
    
    # Try built-in display first
    try:
        display = board.DISPLAY
        print("✓ board.DISPLAY found")
    except:
        # Manual init - check Waveshare examples for your board
        print("✗ board.DISPLAY not found - need manual init")
        print("Check: https://www.waveshare.com/wiki/RP2350-Touch-LCD-1.85C")
        display = None
    
    if display:
        splash = displayio.Group()
        text = label.Label(terminalio.FONT, text="Magic Orb Ready!", scale=2, color=0x00FFFF)
        text.anchor_point = (0.5, 0.5)
        text.anchored_position = (display.width // 2, display.height // 2)
        splash.append(text)
        display.show(splash)
        print("✓ Display showing text")
        
except Exception as e:
    print(f"✗ Display error: {e}")

# Test 3: Touch (placeholder)
print("\nTouch: TODO - check Waveshare examples for touch driver")

# Test 4: Audio (placeholder)
print("\nAudio: TODO - need to identify mic/speaker hardware config")

print("\n=== Tests Complete ===")
print("Next steps:")
print("1. Get display working with Waveshare examples")
print("2. Identify touch controller (CST816S? GT911?)")
print("3. Wire up audio (I2S? Analog?)")
print("4. Then add PTT functionality")
