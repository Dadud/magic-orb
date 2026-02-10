"""Stage A canonical validation: display-only path."""
import sys
import time

from hardware_profile import (
    BOARD_NAME,
    DISPLAY_BUS_TYPE,
    DISPLAY_CONTROLLER,
    DISPLAY_DRIVER,
    DISPLAY_DRIVER_STATUS,
)

sys.path.append('/lib')
from st77916 import ST77916

print("🔮 Magic Orb - Stage A (Display-Only)")
print("=" * 44)
print("Canonical script: test_display.py")
print(f"Board: {BOARD_NAME}")
print(f"Display: {DISPLAY_CONTROLLER} over {DISPLAY_BUS_TYPE}")
print(f"Driver: {DISPLAY_DRIVER} ({DISPLAY_DRIVER_STATUS})")
print("Failure signature if display does not init: display init timeout")

print("\n[Stage A] Initializing display...")
start_ms = time.ticks_ms()
display = ST77916()
elapsed_ms = time.ticks_diff(time.ticks_ms(), start_ms)

if elapsed_ms > 5000:
    raise RuntimeError(f"display init timeout: {elapsed_ms}ms")

print(f"✓ Display initialized in {elapsed_ms}ms")

print("\n[Stage A] Rendering color sweep...")
for color, name in [
    (display.RED, "RED"),
    (display.GREEN, "GREEN"),
    (display.BLUE, "BLUE"),
    (display.WHITE, "WHITE"),
    (display.BLACK, "BLACK"),
]:
    print(f"  -> {name}")
    display.fill(color)
    display.show()
    time.sleep(0.35)

print("\n[Stage A] Rendering text + geometry...")
display.fill(display.BLACK)
display.text("Magic Orb", 120, 160, display.CYAN)
display.text("Stage A PASS", 110, 190, display.WHITE)
for step in range(0, 160, 8):
    display.pixel(180 + step // 2, 180, display.MAGENTA)
    display.pixel(180 - step // 2, 180, display.MAGENTA)
display.show()

print("\n✓ Stage A PASS")
print("Proceed to Stage B only after visual checks match TESTING.md.")
