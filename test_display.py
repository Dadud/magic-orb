# Magic Orb - Display Test
# Tests the round 360x360 display
from machine import Pin, SPI
import time
import sys
sys.path.append('/lib')
from gc9a01 import GC9A01

print("🔮 Magic Orb - Display Test")
print("=" * 30)

# Pin configuration for RP2350-Touch-LCD-1.85C
# These are typical pins - may need adjustment
LCD_DC   = 8   # Data/Command
LCD_CS   = 9   # Chip Select
LCD_SCK  = 10  # SPI Clock
LCD_MOSI = 11  # SPI MOSI
LCD_MISO = 12  # SPI MISO (not used for display)
LCD_BL   = 13  # Backlight
LCD_RST  = 15  # Reset

# Initialize SPI
print("\nInitializing SPI...")
spi = SPI(
    1,              # SPI instance
    60000000,       # 60MHz clock
    sck=Pin(LCD_SCK),
    mosi=Pin(LCD_MOSI),
    miso=Pin(LCD_MISO)
)

# Initialize display
print("Initializing display...")
display = GC9A01(
    spi=spi,
    dc=Pin(LCD_DC, Pin.OUT),
    cs=Pin(LCD_CS, Pin.OUT),
    rst=Pin(LCD_RST, Pin.OUT),
    bl=Pin(LCD_BL, Pin.OUT)
)

print("✓ Display initialized!")

# Test: Fill with colors
print("\nTest 1: Fill screen with colors...")
colors = [
    (display.RED, "RED"),
    (display.GREEN, "GREEN"),
    (display.BLUE, "BLUE"),
    (display.WHITE, "WHITE"),
    (display.BLACK, "BLACK"),
]

for color, name in colors:
    print(f"  Filling {name}...")
    display.fill(color)
    display.show()
    time.sleep(0.5)

# Test: Draw text
print("\nTest 2: Drawing text...")
display.fill(display.BLACK)
display.text("Magic Orb", 120, 170, display.CYAN)
display.text("Ready!", 140, 200, display.WHITE)
display.show()
time.sleep(2)

# Test: Draw shapes
print("\nTest 3: Drawing shapes...")
display.fill(display.BLACK)
# Center circle
center_x = 180
center_y = 180
for r in range(10, 150, 20):
    color = display.CYAN if (r // 20) % 2 == 0 else display.MAGENTA
    # Draw circle (as points - framebuf doesn't have circle)
    for angle in range(0, 360, 5):
        import math
        x = int(center_x + r * math.cos(math.radians(angle)))
        y = int(center_y + r * math.sin(math.radians(angle)))
        if 0 <= x < 360 and 0 <= y < 360:
            display.pixel(x, y, color)

display.text("Magic Orb", 130, 170, display.WHITE)
display.show()

print("\n✓ All tests passed!")
print("Display is working correctly.")
print("\nNext: Test WiFi with all_in_one_test.py")
