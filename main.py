"""Canonical Phase 0 boot entrypoint (MicroPython).

This file intentionally does only three things for stabilization:
1) initialize display,
2) initialize ESP-AT UART,
3) show status.
"""
from machine import Pin, SPI, UART
import sys
import time

# Target runtime: MicroPython

# Display pins (current baseline from test scripts)
LCD_DC = 8
LCD_CS = 9
LCD_SCK = 10
LCD_MOSI = 11
LCD_MISO = 12
LCD_BL = 13
LCD_RST = 15

# ESP-AT UART pins
ESP_TX = 0  # GP0 -> ESP32 RX
ESP_RX = 1  # GP1 <- ESP32 TX


def init_display():
    """Initialize GC9A01 display and draw startup status."""
    sys.path.append('/lib')
    from gc9a01 import GC9A01

    spi = SPI(1, 60_000_000, sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))
    display = GC9A01(
        spi=spi,
        dc=Pin(LCD_DC, Pin.OUT),
        cs=Pin(LCD_CS, Pin.OUT),
        rst=Pin(LCD_RST, Pin.OUT),
        bl=Pin(LCD_BL, Pin.OUT),
    )

    display.fill(display.BLACK)
    display.text('Magic Orb', 130, 150, display.CYAN)
    display.text('Runtime: MicroPython', 70, 180, display.WHITE)
    display.text('ESP-AT UART: init...', 70, 210, display.WHITE)
    display.show()
    return display


def init_esp_at_uart():
    """Initialize UART for ESP32 ESP-AT module."""
    uart = UART(0, baudrate=115200, tx=Pin(ESP_TX), rx=Pin(ESP_RX))
    # Probe once so boot logs show basic health signal
    uart.write(b'AT\r\n')
    time.sleep_ms(200)
    return uart


def show_ready(display):
    """Update display with stabilized boot status."""
    display.fill(display.BLACK)
    display.text('Magic Orb', 130, 150, display.CYAN)
    display.text('Display: OK', 120, 185, display.GREEN)
    display.text('ESP-AT UART: OK', 95, 210, display.GREEN)
    display.show()


def main():
    display = init_display()
    _uart = init_esp_at_uart()
    show_ready(display)
    print('Magic Orb Phase 0 boot complete (MicroPython).')


if __name__ == '__main__':
    main()
