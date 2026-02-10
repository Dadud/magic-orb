# Simple display test - just backlight + GPIO check
from machine import Pin
import time

print("Simple hardware test...")

# Backlight
bl = Pin(24, Pin.OUT)
bl(1)  # Turn on backlight
print("Backlight ON - screen should glow")

# Reset pulse
rst = Pin(16, Pin.OUT)
rst(0)
time.sleep(0.1)
rst(1)
print("Reset pulse sent")

# Check if we can at least toggle CS
cs = Pin(15, Pin.OUT)
for i in range(5):
    cs(0)
    time.sleep(0.1)
    cs(1)
    time.sleep(0.1)

print("CS toggled 5 times")
print("\nIf screen is glowing, hardware is working.")
print("The issue is the QSPI driver being too complex for MicroPython.")
print("\nOptions:")
print("1. Use C (Waveshare demo works)")
print("2. Find simpler MicroPython driver")
print("3. Wait for me to debug the PIO code")
