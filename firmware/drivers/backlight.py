"""Backlight control for the RP2350-Touch-LCD-1.85C."""
from machine import Pin, PWM


class Backlight:
    """PWM backlight driver with percentage API."""

    def __init__(self, pin: int, pwm_freq_hz: int, pwm_wrap: int):
        self._pin = Pin(pin, Pin.OUT)
        self._pwm = PWM(self._pin)
        self._pwm.freq(pwm_freq_hz)
        self._pwm_wrap = pwm_wrap
        self._pwm_max = 65535

    def set_percent(self, percent: int) -> None:
        """Set brightness in [0, 100]."""
        if percent < 0:
            percent = 0
        elif percent > 100:
            percent = 100
        duty = int((percent / 100) * self._pwm_max)
        self._pwm.duty_u16(duty)

    def off(self) -> None:
        self.set_percent(0)

    def deinit(self) -> None:
        self._pwm.deinit()
