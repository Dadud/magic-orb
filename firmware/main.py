"""Clean application entrypoint for RP2350-Touch-LCD-1.85C.

This main file contains framework logic only:
- initialize board drivers
- run a non-blocking loop
- update a tiny diagnostics UI
- report touch coordinates over USB REPL
"""
from machine import Pin
import time

from board import config, pins
from drivers.backlight import Backlight
from drivers.display import ST77916
from drivers.touch import CST816


class FirmwareApp:
    """Minimal firmware shell suitable as an app-development base."""

    def __init__(self):
        self.display = None
        self.touch = None
        self.backlight = None

        self._last_touch_ms = 0
        self._last_heartbeat_ms = 0
        self._heartbeat_on = False

    def setup(self):
        # Backlight first so display output is visible after init completes.
        self.backlight = Backlight(
            pin=pins.LCD_BL,
            pwm_freq_hz=config.BACKLIGHT_PWM_FREQ_HZ,
            pwm_wrap=config.BACKLIGHT_PWM_WRAP,
        )
        self.backlight.set_percent(config.BACKLIGHT_DEFAULT_PERCENT)

        self.display = ST77916(
            width=config.DISPLAY_WIDTH,
            height=config.DISPLAY_HEIGHT,
            rotation=config.DISPLAY_ROTATION,
            qspi_freq_hz=config.DISPLAY_QSPI_FREQ_HZ,
            reset_low_ms=config.DISPLAY_RESET_LOW_MS,
            reset_high_ms=config.DISPLAY_RESET_HIGH_MS,
            post_init_ms=config.DISPLAY_POST_INIT_MS,
            pin_sclk=pins.LCD_SCLK,
            pin_d0=pins.LCD_D0,
            pin_d1=pins.LCD_D1,
            pin_d2=pins.LCD_D2,
            pin_d3=pins.LCD_D3,
            pin_cs=pins.LCD_CS,
            pin_rst=pins.LCD_RST,
            pin_te=pins.LCD_TE,
        )

        self.touch = CST816(
            i2c_id=pins.TOUCH_I2C_ID,
            sda_pin=pins.TOUCH_SDA,
            scl_pin=pins.TOUCH_SCL,
            i2c_freq_hz=config.TOUCH_I2C_FREQ_HZ,
            address=pins.TOUCH_ADDR,
            rst_pin=pins.TOUCH_RST,
            int_pin=pins.TOUCH_INT,
            width=config.DISPLAY_WIDTH,
            height=config.DISPLAY_HEIGHT,
            rotation=config.DISPLAY_ROTATION,
            reset_low_ms=config.TOUCH_RESET_LOW_MS,
            reset_boot_ms=config.TOUCH_RESET_BOOT_MS,
            data_start_reg=config.TOUCH_DATA_START_REG,
            chip_id_reg=config.TOUCH_CHIP_ID_REG,
            expected_chip_id=config.TOUCH_EXPECTED_CHIP_ID,
            sleep_reg=config.TOUCH_SLEEP_REG,
            sleep_off_value=config.TOUCH_SLEEP_OFF,
        )
        chip_id = self.touch.init()

        self._draw_startup(chip_id, self.touch.validate())
        print("[init] display OK")
        print("[init] touch chip id: 0x{:02X}".format(chip_id))

    def _draw_startup(self, chip_id: int, touch_ok: bool):
        d = self.display
        d.fill(ST77916.COLOR_BLACK)
        d.text("RP2350-Touch-LCD-1.85C", 58, 20, ST77916.COLOR_CYAN)
        d.text("MicroPython clean base", 76, 40, ST77916.COLOR_WHITE)

        d.text("Display: ST77916", 106, 80, ST77916.COLOR_GREEN)
        d.text("Touch: CST816", 116, 98, ST77916.COLOR_GREEN if touch_ok else ST77916.COLOR_YELLOW)
        d.text("ID: 0x{:02X}".format(chip_id), 140, 116, ST77916.COLOR_WHITE)

        # Simple shape to validate draw path.
        d.rect(40, 150, 280, 140, ST77916.COLOR_BLUE)
        d.fill_rect(50, 160, 260, 120, ST77916.COLOR_BLACK)
        d.text("Touch the screen", 120, 208, ST77916.COLOR_WHITE)
        d.text("coords print to REPL", 86, 228, ST77916.COLOR_MAGENTA)
        d.show()

    def _update_heartbeat(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_heartbeat_ms) < config.UI_HEARTBEAT_INTERVAL_MS:
            return

        self._last_heartbeat_ms = now
        self._heartbeat_on = not self._heartbeat_on

        color = ST77916.COLOR_GREEN if self._heartbeat_on else ST77916.COLOR_BLUE
        self.display.fill_rect(164, 300, 32, 32, color)
        self.display.show()

    def _poll_touch(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_touch_ms) < config.TOUCH_SAMPLE_INTERVAL_MS:
            return

        self._last_touch_ms = now
        point = self.touch.read_point()
        if point is None:
            return

        x, y = point
        print("touch: x={}, y={}".format(x, y))

        self.display.fill_rect(80, 260, 200, 24, ST77916.COLOR_BLACK)
        self.display.text("x={:03d} y={:03d}".format(x, y), 118, 266, ST77916.COLOR_YELLOW)
        self.display.show()

    def run(self):
        self.setup()
        while True:
            self._poll_touch()
            self._update_heartbeat()
            time.sleep_ms(config.MAIN_LOOP_INTERVAL_MS)


def main():
    app = FirmwareApp()
    app.run()


if __name__ == "__main__":
    main()
