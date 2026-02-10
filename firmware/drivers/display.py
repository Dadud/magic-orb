"""ST77916 display driver for Waveshare RP2350-Touch-LCD-1.85C.

This driver follows the Waveshare BSP pin mapping and command initialization path,
while providing a MicroPython-friendly FrameBuffer API.
"""
import framebuf
from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
import time


@asm_pio(
    sideset_init=PIO.OUT_LOW,
    out_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW),
    out_shiftdir=PIO.SHIFT_RIGHT,
    autopull=True,
    pull_thresh=8,
)
def qspi_4bit():
    out(pins, 4).side(0) [1]
    nop().side(1) [1]


class ST77916(framebuf.FrameBuffer):
    """ST77916 frame-buffered driver using RP2350 PIO for 4-bit serial writes."""

    COLOR_BLACK = 0x0000
    COLOR_WHITE = 0xFFFF
    COLOR_RED = 0xF800
    COLOR_GREEN = 0x07E0
    COLOR_BLUE = 0x001F
    COLOR_CYAN = 0x07FF
    COLOR_MAGENTA = 0xF81F
    COLOR_YELLOW = 0xFFE0

    def __init__(
        self,
        width,
        height,
        rotation,
        qspi_freq_hz,
        reset_low_ms,
        reset_high_ms,
        post_init_ms,
        pin_sclk,
        pin_d0,
        pin_d1,
        pin_d2,
        pin_d3,
        pin_cs,
        pin_rst,
        pin_te,
    ):
        self.width = width
        self.height = height
        self._rotation = rotation
        self._reset_low_ms = reset_low_ms
        self._reset_high_ms = reset_high_ms
        self._post_init_ms = post_init_ms

        self.cs = Pin(pin_cs, Pin.OUT, value=1)
        self.rst = Pin(pin_rst, Pin.OUT, value=1)
        self.te = Pin(pin_te, Pin.IN, Pin.PULL_UP)

        self.sclk = Pin(pin_sclk, Pin.OUT)
        self.d0 = Pin(pin_d0, Pin.OUT)
        self.d1 = Pin(pin_d1, Pin.OUT)
        self.d2 = Pin(pin_d2, Pin.OUT)
        self.d3 = Pin(pin_d3, Pin.OUT)

        self._sm = StateMachine(
            0,
            qspi_4bit,
            freq=qspi_freq_hz,
            sideset_base=Pin(pin_sclk),
            out_base=Pin(pin_d0),
        )
        self._sm.active(1)

        self._buffer = bytearray(self.width * self.height * 2)
        super().__init__(self._buffer, self.width, self.height, framebuf.RGB565)

        self._reset()
        self._init_panel()

    def _reset(self):
        self.rst.value(0)
        time.sleep_ms(self._reset_low_ms)
        self.rst.value(1)
        time.sleep_ms(self._reset_high_ms)

    def _write_byte_1bit(self, value: int):
        for bit_index in range(8):
            self.sclk.value(0)
            bit = (value >> (7 - bit_index)) & 0x01
            self.d0.value(bit)
            self.sclk.value(1)

    def _write_cmd(self, cmd: int, data=None, delay_ms=0, keep_cs=False):
        self.cs.value(0)
        cmd_bytes = bytes((0x02, 0x00, cmd, 0x00))
        for b in cmd_bytes:
            self._write_byte_1bit(b)

        if data:
            for b in data:
                self._write_byte_1bit(b)

        if not keep_cs:
            self.cs.value(1)

        if delay_ms > 0:
            time.sleep_ms(delay_ms)

    def _write_bytes_4bit(self, payload: bytearray):
        for i in range(0, len(payload), 2):
            b1 = payload[i]
            if i + 1 < len(payload):
                b2 = payload[i + 1]
                packed = (
                    ((b1 >> 4) & 0x0F)
                    | ((b1 & 0x0F) << 4)
                    | (((b2 >> 4) & 0x0F) << 8)
                    | ((b2 & 0x0F) << 12)
                )
            else:
                packed = ((b1 >> 4) & 0x0F) | ((b1 & 0x0F) << 4)
            self._sm.put(packed)

    def _init_panel(self):
        # Exact startup sequence used by Waveshare BSP (trimmed to the active set used in their main init path).
        init_cmds = (
            (0xF0, (0x28,), 0), (0xF2, (0x28,), 0), (0x73, (0xF0,), 0), (0x7C, (0xD1,), 0),
            (0x83, (0xE0,), 0), (0x84, (0x61,), 0), (0xF2, (0x82,), 0), (0xF0, (0x00,), 0),
            (0xF0, (0x01,), 0), (0xF1, (0x01,), 0), (0xB0, (0x56,), 0), (0xB1, (0x4D,), 0),
            (0xB2, (0x24,), 0), (0xB4, (0x87,), 0), (0xB5, (0x44,), 0), (0xB6, (0x8B,), 0),
            (0xB7, (0x40,), 0), (0xB8, (0x86,), 0), (0xBA, (0x00,), 0), (0xBB, (0x08,), 0),
            (0xBC, (0x08,), 0), (0xBD, (0x00,), 0), (0xC0, (0x80,), 0), (0xC1, (0x10,), 0),
            (0xC2, (0x37,), 0), (0xC3, (0x80,), 0), (0xC4, (0x10,), 0), (0xC5, (0x37,), 0),
            (0xC6, (0xA9,), 0), (0xC7, (0x41,), 0), (0xC8, (0x01,), 0), (0xC9, (0xA9,), 0),
            (0xCA, (0x41,), 0), (0xCB, (0x01,), 0), (0xD0, (0x91,), 0), (0xD1, (0x68,), 0),
            (0xD2, (0x68,), 0), (0xF5, (0x00, 0xA5), 0), (0xDD, (0x4F,), 0), (0xDE, (0x4F,), 0),
            (0xF1, (0x10,), 0), (0xF0, (0x00,), 0), (0xF0, (0x02,), 0),
            (0xE0, (0xF0, 0x0A, 0x10, 0x09, 0x09, 0x36, 0x35, 0x33, 0x4A, 0x29, 0x15, 0x15, 0x2E, 0x34), 0),
            (0xE1, (0xF0, 0x0A, 0x0F, 0x08, 0x08, 0x05, 0x34, 0x33, 0x4A, 0x39, 0x15, 0x15, 0x2D, 0x33), 0),
            (0xF0, (0x10,), 0), (0xF3, (0x10,), 0), (0xE0, (0x07,), 0), (0xE1, (0x00,), 0),
            (0xE2, (0x00,), 0), (0xE3, (0x00,), 0), (0xE4, (0xE0,), 0), (0xE5, (0x06,), 0),
            (0xE6, (0x21,), 0), (0xE7, (0x01,), 0), (0xE8, (0x05,), 0), (0xE9, (0x02,), 0),
            (0xEA, (0xDA,), 0), (0xEB, (0x00,), 0), (0xEC, (0x00,), 0), (0xED, (0x0F,), 0),
            (0xEE, (0x00,), 0), (0xEF, (0x00,), 0), (0xF8, (0x00,), 0), (0xF9, (0x00,), 0),
            (0xFA, (0x00,), 0), (0xFB, (0x00,), 0), (0xFC, (0x00,), 0), (0xFD, (0x00,), 0),
            (0xFE, (0x00,), 0), (0xFF, (0x00,), 0),
            (0x60, (0x40,), 0), (0x61, (0x04,), 0), (0x62, (0x00,), 0), (0x63, (0x42,), 0),
            (0x64, (0xD9,), 0), (0x65, (0x00,), 0), (0x66, (0x00,), 0), (0x67, (0x00,), 0),
            (0x68, (0x00,), 0), (0x69, (0x00,), 0), (0x6A, (0x00,), 0), (0x6B, (0x00,), 0),
            (0x70, (0x40,), 0), (0x71, (0x03,), 0), (0x72, (0x00,), 0), (0x73, (0x42,), 0),
            (0x74, (0xD8,), 0), (0x75, (0x00,), 0), (0x76, (0x00,), 0), (0x77, (0x00,), 0),
            (0x78, (0x00,), 0), (0x79, (0x00,), 0), (0x7A, (0x00,), 0), (0x7B, (0x00,), 0),
            (0x80, (0x48,), 0), (0x81, (0x00,), 0), (0x82, (0x06,), 0), (0x83, (0x02,), 0),
            (0x84, (0xD6,), 0), (0x85, (0x04,), 0), (0x86, (0x00,), 0), (0x87, (0x00,), 0),
            (0x88, (0x48,), 0), (0x89, (0x00,), 0), (0x8A, (0x08,), 0), (0x8B, (0x02,), 0),
            (0x8C, (0xD8,), 0), (0x8D, (0x04,), 0), (0x8E, (0x00,), 0), (0x8F, (0x00,), 0),
            (0x90, (0x48,), 0), (0x91, (0x00,), 0), (0x92, (0x0A,), 0), (0x93, (0x02,), 0),
            (0x94, (0xDA,), 0), (0x95, (0x04,), 0), (0x96, (0x00,), 0), (0x97, (0x00,), 0),
            (0x98, (0x48,), 0), (0x99, (0x00,), 0), (0x9A, (0x0C,), 0), (0x9B, (0x02,), 0),
            (0x9C, (0xDC,), 0), (0x9D, (0x04,), 0), (0x9E, (0x00,), 0), (0x9F, (0x00,), 0),
            (0xA0, (0x48,), 0), (0xA1, (0x00,), 0), (0xA2, (0x0E,), 0), (0xA3, (0x02,), 0),
            (0xA4, (0xDE,), 0), (0xA5, (0x04,), 0), (0xA6, (0x00,), 0), (0xA7, (0x00,), 0),
            (0xA8, (0x48,), 0), (0xA9, (0x00,), 0), (0xAA, (0x10,), 0), (0xAB, (0x02,), 0),
            (0xAC, (0xE0,), 0), (0xAD, (0x04,), 0), (0xAE, (0x00,), 0), (0xAF, (0x00,), 0),
            (0xB0, (0x48,), 0), (0xB1, (0x00,), 0), (0xB2, (0x12,), 0), (0xB3, (0x02,), 0),
            (0xB4, (0xE2,), 0), (0xB5, (0x04,), 0), (0xB6, (0x00,), 0), (0xB7, (0x00,), 0),
            (0xB8, (0x48,), 0), (0xB9, (0x00,), 0), (0xBA, (0x14,), 0), (0xBB, (0x02,), 0),
            (0xBC, (0xE4,), 0), (0xBD, (0x04,), 0), (0xBE, (0x00,), 0), (0xBF, (0x00,), 0),
            (0xC0, (0x48,), 0), (0xC1, (0x00,), 0), (0xC2, (0x16,), 0), (0xC3, (0x02,), 0),
            (0xC4, (0xE6,), 0), (0xC5, (0x04,), 0), (0xC6, (0x00,), 0), (0xC7, (0x00,), 0),
            (0xC8, (0x48,), 0), (0xC9, (0x00,), 0), (0xCA, (0x18,), 0), (0xCB, (0x02,), 0),
            (0xCC, (0xE8,), 0), (0xCD, (0x04,), 0), (0xCE, (0x00,), 0), (0xCF, (0x00,), 0),
            (0xD0, (0x48,), 0), (0xD1, (0x00,), 0), (0xD2, (0x1A,), 0), (0xD3, (0x02,), 0),
            (0xD4, (0xEA,), 0), (0xD5, (0x04,), 0), (0xD6, (0x00,), 0), (0xD7, (0x00,), 0),
            (0xD8, (0x48,), 0), (0xD9, (0x00,), 0), (0xDA, (0x1C,), 0), (0xDB, (0x02,), 0),
            (0xDC, (0xEC,), 0), (0xDD, (0x04,), 0), (0xDE, (0x00,), 0), (0xDF, (0x00,), 0),
            (0x36, (self._rotation & 0x03,), 0),
            (0x3A, (0x55,), 0),
            (0x21, (), 0),
            (0x11, (), 120),
            (0x29, (), self._post_init_ms),
        )

        for cmd, data, delay in init_cmds:
            self._write_cmd(cmd, bytes(data) if data else None, delay)

    def set_window(self, x1, y1, x2, y2):
        self._write_cmd(0x2A, bytes(((x1 >> 8) & 0xFF, x1 & 0xFF, (x2 >> 8) & 0xFF, x2 & 0xFF)))
        self._write_cmd(0x2B, bytes(((y1 >> 8) & 0xFF, y1 & 0xFF, (y2 >> 8) & 0xFF, y2 & 0xFF)))

    def show(self):
        self.set_window(0, 0, self.width - 1, self.height - 1)
        self._write_cmd(0x2C, keep_cs=True)
        self._write_bytes_4bit(self._buffer)
        self.cs.value(1)
