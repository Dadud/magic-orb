# Magic Orb - Display Test
# Tests the round 360x360 display
import time

from hardware_profile import (
    BOARD_NAME,
    DISPLAY_BUS_TYPE,
    DISPLAY_CONTROLLER,
    DISPLAY_DRIVER,
    DISPLAY_DRIVER_STATUS,
)

import sys
sys.path.append('/lib')
from st77916 import ST77916

print("🔮 Magic Orb - Display Test")
print("=" * 30)
print(f"Board: {BOARD_NAME}")
print(f"Display: {DISPLAY_CONTROLLER} over {DISPLAY_BUS_TYPE}")
print(f"Driver: {DISPLAY_DRIVER} ({DISPLAY_DRIVER_STATUS})")

print("\nInitializing display...")
display = ST77916()
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
center_x = 180
center_y = 180
for r in range(10, 150, 20):
    color = display.CYAN if (r // 20) % 2 == 0 else display.MAGENTA
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
print("\nNext: Test WiFi with test_complete.py")
