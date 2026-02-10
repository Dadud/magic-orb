# ST77916 QSPI Display Driver for RP2350-Touch-LCD-1.85C
# Phase 0 primary display driver (authoritative profile uses QSPI + ST77916)
# Based on Waveshare RP2350-Touch-LCD-1.85C-Demo
# Uses PIO for 4-wire SPI (QSPI)
import machine
import time
import framebuf
from rp2 import PIO, StateMachine, asm_pio

# Pin configuration from Waveshare demo
LCD_SCLK = 10
LCD_D0   = 11
LCD_D1   = 12
LCD_D2   = 13
LCD_D3   = 14
LCD_CS   = 15
LCD_RST  = 16
LCD_TE   = 17
LCD_BL   = 24

# QSPI PIO program - outputs 4 bits at a time
@asm_pio(sideset_init=PIO.OUT_LOW, out_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW),
         out_shiftdir=PIO.SHIFT_RIGHT, autopull=True, pull_thresh=8)
def qspi_prog():
    # Toggle SCLK using sideset while shifting 4-bit nibbles on D0..D3.
    out(pins, 4).side(0)  [1]  # Clock low, output nibble
    nop().side(1)         [1]  # Clock high

class ST77916(framebuf.FrameBuffer):
    """ST77916 360x360 round display with QSPI interface"""

    def __init__(self):
        self.width = 360
        self.height = 360

        # Setup GPIOs
        self.cs = machine.Pin(LCD_CS, machine.Pin.OUT, value=1)
        self.rst = machine.Pin(LCD_RST, machine.Pin.OUT, value=1)
        self.bl = machine.Pin(LCD_BL, machine.Pin.OUT, value=0)
        self.te = machine.Pin(LCD_TE, machine.Pin.IN, machine.Pin.PULL_UP)

        # Data pins for QSPI
        self.d0 = machine.Pin(LCD_D0, machine.Pin.OUT)
        self.d1 = machine.Pin(LCD_D1, machine.Pin.OUT)
        self.d2 = machine.Pin(LCD_D2, machine.Pin.OUT)
        self.d3 = machine.Pin(LCD_D3, machine.Pin.OUT)
        self.sclk = machine.Pin(LCD_SCLK, machine.Pin.OUT)

        # Initialize QSPI state machine
        self.sm = StateMachine(0, qspi_prog,
                              freq=80_000_000,
                              sideset_base=machine.Pin(LCD_SCLK),
                              out_base=machine.Pin(LCD_D0))
        self.sm.active(1)

        # Framebuffer (RGB565)
        self.buffer = bytearray(self.width * self.height * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)

        # Colors
        self.RED = 0xF800
        self.GREEN = 0x07E0
        self.BLUE = 0x001F
        self.WHITE = 0xFFFF
        self.BLACK = 0x0000
        self.CYAN = 0x07FF
        self.MAGENTA = 0xF81F
        self.YELLOW = 0xFFE0

        # Initialize display
        self._init_display()
        self.bl(1)  # Turn on backlight

    def _write_cmd(self, cmd, data=None, delay=0, keep_cs=False):
        """Write command and optional data"""
        self.cs(0)

        # Command phase (1-bit mode): 0x02, 0x00, cmd, 0x00
        cmd_bytes = bytes([0x02, 0x00, cmd, 0x00])

        # Use regular GPIO for command phase
        for b in cmd_bytes:
            self._write_byte_1bit(b)

        # Data phase if needed
        if data:
            for b in data:
                self._write_byte_1bit(b)

        if not keep_cs:
            self.cs(1)

        if delay:
            time.sleep_ms(delay)

    def _write_byte_1bit(self, byte):
        """Write a byte in 1-bit mode (bit-banging for simplicity)"""
        for i in range(8):
            self.sclk(0)
            # Set data bit on D0
            bit = (byte >> (7-i)) & 1
            self.d0(bit)
            self.sclk(1)

    def _write_bytes_4bit(self, data):
        """Write bytes using QSPI 4-bit mode"""
        # Pack nibbles for 4-bit transfer
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                # Two bytes become 4 nibbles
                byte1 = data[i]
                byte2 = data[i+1]
                # Pack: high nibble of byte1, low nibble of byte1, etc.
                word = ((byte1 >> 4) & 0xF) | ((byte1 & 0xF) << 4) | ((byte2 >> 4) & 0xF) << 8 | ((byte2 & 0xF) << 12)
                self.sm.put(word)
            else:
                # Last byte
                byte1 = data[i]
                word = ((byte1 >> 4) & 0xF) | ((byte1 & 0xF) << 4)
                self.sm.put(word)

    def _init_display(self):
        """Initialize ST77916 display"""
        # Reset
        self.rst(0)
        time.sleep_ms(100)
        self.rst(1)
        time.sleep_ms(100)

        # Init sequence from Waveshare demo
        init_cmds = [
            (0xF0, [0x28], 0),
            (0xF2, [0x28], 0),
            (0x73, [0xF0], 0),
            (0x7C, [0xD1], 0),
            (0x83, [0xE0], 0),
            (0x84, [0x61], 0),
            (0xF2, [0x82], 0),
            (0xF0, [0x00], 0),
            (0xF0, [0x01], 0),
            (0xF1, [0x01], 0),
            (0xB0, [0x56], 0),
            (0xB1, [0x4D], 0),
            (0xB2, [0x24], 0),
            (0xB4, [0x87], 0),
            (0xB5, [0x44], 0),
            (0xB6, [0x8B], 0),
            (0xB7, [0x40], 0),
            (0xB8, [0x86], 0),
            (0xBA, [0x00], 0),
            (0xBB, [0x08], 0),
            (0xBC, [0x08], 0),
            (0xBD, [0x00], 0),
            (0xC0, [0x80], 0),
            (0xC1, [0x10], 0),
            (0xC2, [0x37], 0),
            (0xC3, [0x80], 0),
            (0xC4, [0x10], 0),
            (0xC5, [0x37], 0),
            (0xC6, [0xA9], 0),
            (0xC7, [0x41], 0),
            (0xC8, [0x01], 0),
            (0xC9, [0xA9], 0),
            (0xCA, [0x41], 0),
            (0xCB, [0x01], 0),
            (0xD0, [0x91], 0),
            (0xD1, [0x08], 0),
            (0xD2, [0x88], 0),
            (0xD3, [0x88], 0),
            (0xD4, [0x88], 0),
            (0xD5, [0x88], 0),
            (0xE0, [0x00, 0x03, 0x07, 0x0E, 0x13, 0x17, 0x1B, 0x1E, 0x1F, 0x1D, 0x1A, 0x15, 0x0F, 0x0A, 0x05, 0x01], 0),
            (0xE1, [0x1F, 0x1C, 0x18, 0x11, 0x0C, 0x08, 0x04, 0x01, 0x00, 0x02, 0x05, 0x0A, 0x10, 0x15, 0x1A, 0x1E], 0),
            (0x35, [0x00], 0),
            (0x36, [0x00], 0),  # Rotation
            (0x3A, [0x55], 0),  # 16-bit color
            (0x21, [], 0),      # Inversion on
            (0x11, [], 120),    # Sleep out
            (0x29, [], 20),     # Display on
        ]

        for cmd, data, delay in init_cmds:
            self._write_cmd(cmd, bytes(data) if data else None, delay)

    def _set_window(self, x1, y1, x2, y2):
        """Set drawing window"""
        self._write_cmd(0x2A, bytes([
            (x1 >> 8) & 0xFF, x1 & 0xFF,
            (x2 >> 8) & 0xFF, x2 & 0xFF
        ]))
        self._write_cmd(0x2B, bytes([
            (y1 >> 8) & 0xFF, y1 & 0xFF,
            (y2 >> 8) & 0xFF, y2 & 0xFF
        ]))

    def show(self):
        """Display the framebuffer"""
        self._set_window(0, 0, self.width - 1, self.height - 1)

        # Start memory write (0x2C), but keep CS asserted while streaming pixels.
        self._write_cmd(0x2C, keep_cs=True)

        # Send pixel data over 4-bit bus.
        self._write_bytes_4bit(self.buffer)

        self.cs(1)
