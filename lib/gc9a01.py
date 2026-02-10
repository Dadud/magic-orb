# GC9A01 Round Display Driver for RP2350-Touch-LCD-1.85C
# Backup/experimental driver (not Phase 0 primary profile)
# 360x360 round display
import machine
import time
import framebuf

class GC9A01(framebuf.FrameBuffer):
    """Driver for GC9A01 360x360 round display"""

    def __init__(self, spi, dc, cs, rst, bl=None, rotation=0):
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.rst = rst
        self.bl = bl
        self.rotation = rotation
        self.width = 360
        self.height = 360

        # Buffer for display (RGB565 = 2 bytes per pixel)
        self.buffer = bytearray(self.width * self.height * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)

        # Initialize pins
        self.cs(1)
        self.dc(1)
        self.rst(1)

        # Colors (RGB565)
        self.RED = 0xF800
        self.GREEN = 0x07E0
        self.BLUE = 0x001F
        self.WHITE = 0xFFFF
        self.BLACK = 0x0000
        self.CYAN = 0x07FF
        self.MAGENTA = 0xF81F
        self.YELLOW = 0xFFE0

        self._init_display()

        # Turn on backlight
        if self.bl:
            self.bl(1)

    def _write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def _write_data(self, data):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        self.cs(1)

    def _init_display(self):
        """Initialize GC9A01 display"""
        # Reset
        self.rst(1)
        time.sleep_ms(100)
        self.rst(0)
        time.sleep_ms(100)
        self.rst(1)
        time.sleep_ms(100)

        # Init sequence for GC9A01
        self._write_cmd(0xEF)
        self._write_cmd(0xEB)
        self._write_data(0x14)

        self._write_cmd(0xFE)
        self._write_cmd(0xEF)

        self._write_cmd(0xEB)
        self._write_data(0x14)

        self._write_cmd(0x84)
        self._write_data(0x40)

        self._write_cmd(0x85)
        self._write_data(0xFF)

        self._write_cmd(0x86)
        self._write_data(0xFF)

        self._write_cmd(0x87)
        self._write_data(0xFF)

        self._write_cmd(0x88)
        self._write_data(0x0A)

        self._write_cmd(0x89)
        self._write_data(0x21)

        self._write_cmd(0x8A)
        self._write_data(0x00)

        self._write_cmd(0x8B)
        self._write_data(0x80)

        self._write_cmd(0x8C)
        self._write_data(0x01)

        self._write_cmd(0x8D)
        self._write_data(0x01)

        self._write_cmd(0x8E)
        self._write_data(0xFF)

        self._write_cmd(0x8F)
        self._write_data(0xFF)

        self._write_cmd(0xB6)
        self._write_data(0x00)
        self._write_data(0x20)

        self._write_cmd(0x36)
        self._write_data(0x08)  # Rotation

        self._write_cmd(0x3A)
        self._write_data(0x05)  # 16-bit color

        self._write_cmd(0x90)
        self._write_data(0x08)
        self._write_data(0x08)
        self._write_data(0x08)
        self._write_data(0x08)

        self._write_cmd(0xBD)
        self._write_data(0x06)

        self._write_cmd(0xBC)
        self._write_data(0x00)

        self._write_cmd(0xFF)
        self._write_data(0x60)
        self._write_data(0x01)
        self._write_data(0x04)

        self._write_cmd(0xC3)
        self._write_data(0x13)
        self._write_cmd(0xC4)
        self._write_data(0x13)

        self._write_cmd(0xC9)
        self._write_data(0x22)

        self._write_cmd(0xBE)
        self._write_data(0x11)

        self._write_cmd(0xE1)
        self._write_data(0x10)
        self._write_data(0x0E)

        self._write_cmd(0xDF)
        self._write_data(0x21)
        self._write_data(0x0c)
        self._write_data(0x02)

        self._write_cmd(0xF0)
        self._write_data(0x45)
        self._write_data(0x09)
        self._write_data(0x08)
        self._write_data(0x08)
        self._write_data(0x26)
        self._write_data(0x2A)

        self._write_cmd(0xF1)
        self._write_data(0x43)
        self._write_data(0x70)
        self._write_data(0x72)
        self._write_data(0x36)
        self._write_data(0x37)
        self._write_data(0x6F)

        self._write_cmd(0xF2)
        self._write_data(0x45)
        self._write_data(0x09)
        self._write_data(0x08)
        self._write_data(0x08)
        self._write_data(0x26)
        self._write_data(0x2A)

        self._write_cmd(0xF3)
        self._write_data(0x43)
        self._write_data(0x70)
        self._write_data(0x72)
        self._write_data(0x36)
        self._write_data(0x37)
        self._write_data(0x6F)

        self._write_cmd(0xED)
        self._write_data(0x1B)
        self._write_data(0x0B)

        self._write_cmd(0xAE)
        self._write_data(0x77)

        self._write_cmd(0xCD)
        self._write_data(0x63)

        self._write_cmd(0x70)
        self._write_data(0x07)
        self._write_data(0x07)
        self._write_data(0x04)
        self._write_data(0x0E)
        self._write_data(0x0F)
        self._write_data(0x09)
        self._write_data(0x07)
        self._write_data(0x08)
        self._write_data(0x03)

        self._write_cmd(0xE8)
        self._write_data(0x34)

        self._write_cmd(0x62)
        self._write_data(0x18)
        self._write_data(0x0D)
        self._write_data(0x71)
        self._write_data(0xED)
        self._write_data(0x70)
        self._write_data(0x70)
        self._write_data(0x18)
        self._write_data(0x0F)
        self._write_data(0x71)
        self._write_data(0xEF)
        self._write_data(0x70)
        self._write_data(0x70)

        self._write_cmd(0x63)
        self._write_data(0x18)
        self._write_data(0x11)
        self._write_data(0x71)
        self._write_data(0xF1)
        self._write_data(0x70)
        self._write_data(0x70)
        self._write_data(0x18)
        self._write_data(0x13)
        self._write_data(0x71)
        self._write_data(0xF3)
        self._write_data(0x70)
        self._write_data(0x70)

        self._write_cmd(0x64)
        self._write_data(0x28)
        self._write_data(0x29)
        self._write_data(0xF1)
        self._write_data(0x01)
        self._write_data(0xF1)
        self._write_data(0x00)
        self._write_data(0x07)

        self._write_cmd(0x66)
        self._write_data(0x3C)
        self._write_data(0x00)
        self._write_data(0xCD)
        self._write_data(0x67)
        self._write_data(0x45)
        self._write_data(0x45)
        self._write_data(0x10)
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data(0x00)

        self._write_cmd(0x67)
        self._write_data(0x00)
        self._write_data(0x3C)
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data(0x01)
        self._write_data(0x54)
        self._write_data(0x10)
        self._write_data(0x32)
        self._write_data(0x98)

        self._write_cmd(0x74)
        self._write_data(0x10)
        self._write_data(0x85)
        self._write_data(0x80)
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data(0x4E)
        self._write_data(0x00)

        self._write_cmd(0x98)
        self._write_data(0x3e)
        self._write_data(0x07)

        self._write_cmd(0x35)
        self._write_data(0x00)

        self._write_cmd(0x21)

        self._write_cmd(0x11)
        time.sleep_ms(120)
        self._write_cmd(0x29)
        time.sleep_ms(20)

    def show(self):
        """Display the buffer"""
        self._write_cmd(0x2A)  # Column address
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data((self.width - 1) >> 8)
        self._write_data((self.width - 1) & 0xFF)

        self._write_cmd(0x2B)  # Row address
        self._write_data(0x00)
        self._write_data(0x00)
        self._write_data((self.height - 1) >> 8)
        self._write_data((self.height - 1) & 0xFF)

        self._write_cmd(0x2C)  # Write memory

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
