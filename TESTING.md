# 🔮 Magic Orb - Phase 0 Testing (MicroPython)

This test guide covers only the selected stabilization runtime: **MicroPython**.

## Test matrix

1. **Boot smoke test**: `main.py`
2. **Display test**: `test_display.py`
3. **Display + ESP-AT test**: `test_complete.py`

## Prerequisites

- `firmware/firmware.uf2` flashed
- Device files copied:
  - `main.py`
  - `lib/gc9a01.py`
- For full test flow, also copy:
  - `test_display.py`
  - `test_complete.py`

## 1) Boot smoke test (`main.py`)

Reboot the board.

**Expected:**
- Display initializes
- ESP-AT UART initializes
- Status text appears on display

## 2) Display validation (`test_display.py`)

Run `test_display.py` from Thonny.

**Expected:**
- Color fill sequence renders
- Text appears on screen
- Basic shape rendering appears

## 3) WiFi + display validation (`test_complete.py`)

Edit credentials in file:

```python
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"
```

Run `test_complete.py`.

**Expected:**
- Display init passes
- ESP32 responds to AT command
- WiFi association succeeds

## Current baseline pins (MicroPython tests)

```python
LCD_DC   = 8
LCD_CS   = 9
LCD_SCK  = 10
LCD_MOSI = 11
LCD_MISO = 12
LCD_BL   = 13
LCD_RST  = 15

ESP_TX   = 0
ESP_RX   = 1
```

## Deferred runtime note

CircuitPython files are kept in-repo for reference but are not part of Phase 0 stabilization or acceptance testing.
