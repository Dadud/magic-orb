"""Magic Orb Phase 0 hardware profile (single tested board profile).

Authoritative source for board/controller/bus/pin constants used by Phase 0
tests and docs. Based on Waveshare RP2350-Touch-LCD-1.85C demo sources.
"""

# Board and display profile
BOARD_NAME = "Waveshare RP2350-Touch-LCD-1.85C"
DISPLAY_CONTROLLER = "ST77916"
DISPLAY_BUS_TYPE = "QSPI"
DISPLAY_DRIVER = "lib/st77916.py"
DISPLAY_DRIVER_STATUS = "phase0-primary"
BACKUP_DISPLAY_DRIVER = "lib/gc9a01.py"
BACKUP_DISPLAY_DRIVER_STATUS = "experimental-backup"

# Display QSPI profile (Waveshare demo)
LCD_SCLK = 10
LCD_D0 = 11
LCD_D1 = 12
LCD_D2 = 13
LCD_D3 = 14
LCD_CS = 15
LCD_RST = 16
LCD_TE = 17
LCD_BL = 24

# ESP32 ESP-AT UART profile (project wiring)
ESP_UART_ID = 0
ESP_UART_BAUDRATE = 115_200
ESP_TX = 0  # GP0 -> ESP32 RX
ESP_RX = 1  # GP1 <- ESP32 TX


def summary():
    """Human-readable profile summary string."""
    return (
        f"{BOARD_NAME}: {DISPLAY_CONTROLLER} over {DISPLAY_BUS_TYPE} "
        f"({DISPLAY_DRIVER}, {DISPLAY_DRIVER_STATUS})"
    )
