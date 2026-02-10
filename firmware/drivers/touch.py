"""CST816 touch controller driver for RP2350-Touch-LCD-1.85C."""
from machine import I2C, Pin
import time


class CST816:
    """Minimal CST816 single-touch polling driver."""

    def __init__(
        self,
        i2c_id: int,
        sda_pin: int,
        scl_pin: int,
        i2c_freq_hz: int,
        address: int,
        rst_pin: int,
        int_pin: int,
        width: int,
        height: int,
        rotation: int,
        reset_low_ms: int,
        reset_boot_ms: int,
        data_start_reg: int,
        chip_id_reg: int,
        expected_chip_id: int,
        sleep_reg: int,
        sleep_off_value: int,
    ):
        self._i2c = I2C(i2c_id, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=i2c_freq_hz)
        self._addr = address
        self._rst = Pin(rst_pin, Pin.OUT)
        self._int = Pin(int_pin, Pin.IN, Pin.PULL_UP)
        self._width = width
        self._height = height
        self._rotation = rotation

        self._reset_low_ms = reset_low_ms
        self._reset_boot_ms = reset_boot_ms
        self._data_start_reg = data_start_reg
        self._chip_id_reg = chip_id_reg
        self._expected_chip_id = expected_chip_id
        self._sleep_reg = sleep_reg
        self._sleep_off = sleep_off_value

        self._chip_id = None

    def _read_reg(self, reg: int, length: int) -> bytes:
        self._i2c.writeto(self._addr, bytes((reg,)), False)
        return self._i2c.readfrom(self._addr, length)

    def _write_reg(self, reg: int, payload: bytes) -> None:
        self._i2c.writeto(self._addr, bytes((reg,)) + payload)

    def reset(self) -> None:
        self._rst.value(0)
        time.sleep_ms(self._reset_low_ms)
        self._rst.value(1)
        time.sleep_ms(self._reset_boot_ms)

    def init(self) -> int:
        """Reset device, wake it, and return chip ID."""
        self.reset()
        self._chip_id = self._read_reg(self._chip_id_reg, 1)[0]
        self._write_reg(self._sleep_reg, bytes((self._sleep_off,)))
        return self._chip_id

    @property
    def chip_id(self):
        return self._chip_id

    def validate(self) -> bool:
        return self._chip_id == self._expected_chip_id

    def _rotate(self, x: int, y: int):
        if self._rotation == 1:
            return y, self._height - 1 - x
        if self._rotation == 2:
            return self._width - 1 - x, self._height - 1 - y
        if self._rotation == 3:
            return self._width - 1 - y, x
        return x, y

    def read_point(self):
        """Return (x, y) when touched, or None.

        Data format mirrors Waveshare BSP read path from register 0x02:
        [num, xh, xl, yh, yl]
        """
        raw = self._read_reg(self._data_start_reg, 5)
        points = raw[0]
        if points == 0:
            return None

        x = ((raw[1] & 0x0F) << 8) | raw[2]
        y = ((raw[3] & 0x0F) << 8) | raw[4]

        if x < 0:
            x = 0
        elif x >= self._width:
            x = self._width - 1

        if y < 0:
            y = 0
        elif y >= self._height:
            y = self._height - 1

        return self._rotate(x, y)
