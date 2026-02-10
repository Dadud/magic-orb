# quick_test.py - Copy this to your device and run
# Tests: Display + WiFi

print("Magic Orb Quick Test")
print("=" * 30)

# Test 1: Display
print("\n1. Testing display...")
try:
    import machine
    import st7789  # Common driver, might need adjustment

    # Basic SPI setup (adjust pins for your board)
    spi = machine.SPI(0, baudrate=60000000, polarity=1, phase=1,
                      sck=machine.Pin(18), mosi=machine.Pin(19))
    display = st7789.ST7789(
        spi, 360, 360,
        reset=machine.Pin(20, machine.Pin.OUT),
        cs=machine.Pin(17, machine.Pin.OUT),
        dc=machine.Pin(16, machine.Pin.OUT),
        backlight=machine.Pin(21, machine.Pin.OUT),
        rotation=0
    )
    display.fill(st7789.color565(0, 0, 255))  # Blue screen
    print("✓ Display works! Should be blue now")
except Exception as e:
    print(f"✗ Display failed: {e}")
    print("  This is normal - need to check Waveshare examples for correct driver/pins")

# Test 2: UART to ESP32
print("\n2. Testing UART to ESP32...")
try:
    from machine import UART, Pin
    import time

    # Adjust pins to your wiring
    uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
    uart.write(b"AT\r\n")
    time.sleep(0.5)

    if uart.any():
        response = uart.read()
        print(f"✓ ESP32 responded: {response}")
    else:
        print("✗ No response - check wiring (ESP TX -> RP2350 RX on GP1)")
except Exception as e:
    print(f"✗ UART failed: {e}")

# Test 3: WiFi via AT commands
print("\n3. Testing WiFi connection...")
try:
    # Simple AT command test
    def send_at(cmd, timeout=2000):
        uart.write((cmd + "\r\n").encode())
        time.sleep_ms(timeout)
        if uart.any():
            return uart.read().decode()
        return None

    # Set station mode
    send_at("AT+CWMODE=1")

    # Connect (replace with your WiFi)
    WIFI_SSID = "YOUR_WIFI_NAME"
    WIFI_PASS = "YOUR_WIFI_PASSWORD"

    print(f"Connecting to {WIFI_SSID}...")
    resp = send_at(f'AT+CWJAP="{WIFI_SSID}","{WIFI_PASS}"', 10000)
    if resp and "OK" in resp:
        print("✓ WiFi connected!")
    else:
        print(f"✗ WiFi failed: {resp}")
except Exception as e:
    print(f"✗ WiFi test failed: {e}")

print("\n" + "=" * 30)
print("Tests complete!")
print("\nIf display failed, check Waveshare examples:")
print("https://github.com/waveshareteam/Pico_MircoPython_Examples")
