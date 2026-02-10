"""Centralized pin definitions for Waveshare RP2350-Touch-LCD-1.85C.

All values are sourced from the official Waveshare C BSP headers:
- libraries/bsp/bsp_st77916.h
- libraries/bsp/bsp_i2c.h
- libraries/bsp/bsp_cst816.h
"""

# Display (ST77916 over 4-line serial/QSPI-like bus)
LCD_SCLK = 10
LCD_D0 = 11
LCD_D1 = 12
LCD_D2 = 13
LCD_D3 = 14
LCD_CS = 15
LCD_RST = 16
LCD_TE = 17
LCD_BL = 24

# Touch (CST816 over I2C1)
TOUCH_I2C_ID = 1
TOUCH_SDA = 6
TOUCH_SCL = 7
TOUCH_RST = 9
TOUCH_INT = 8
TOUCH_ADDR = 0x15
