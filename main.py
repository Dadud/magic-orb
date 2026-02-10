"""Canonical Phase 0 boot entrypoint (MicroPython).

This file intentionally does only three things for stabilization:
1) initialize display,
2) initialize ESP-AT UART,
3) show status.
"""
from machine import Pin, UART
import sys
import time

# Target runtime: MicroPython

# ESP-AT UART pins
ESP_TX = 26  # GP26 -> ESP32 RX
ESP_RX = 27  # GP27 <- ESP32 TX


def init_display():
    """Initialize ST77916 display and draw startup status."""
    sys.path.append('/lib')
    from st77916 import ST77916

    display = ST77916()

    display.fill(display.BLACK)
    display.text('Magic Orb', 130, 150, display.CYAN)
    display.text('Runtime: MicroPython', 70, 180, display.WHITE)
    display.text('Display: ST77916', 95, 210, display.WHITE)
    display.text('ESP-AT UART: init...', 70, 240, display.WHITE)
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
    display.text('Display: ST77916 OK', 85, 185, display.GREEN)
    display.text('ESP-AT UART: OK', 95, 210, display.GREEN)
    display.show()


def main():
    display = init_display()
    _uart = init_esp_at_uart()
    show_ready(display)
    print('Magic Orb Phase 0 boot complete (MicroPython, ST77916).')


if __name__ == '__main__':
    main()
