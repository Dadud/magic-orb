# 🔮 Magic Orb - Ready to Test!

**Status:** Phase 0 uses ST77916 over QSPI as the primary display path (GC9A01 kept as backup/experimental).

## What's New

✅ **ST77916 Driver Selected (Phase 0 Primary)** - `/workspace/magic-orb/lib/st77916.py`
- Matches Waveshare demo controller/bus (ST77916 over QSPI)
- QSPI data lines D0-D3 + control pins as in vendor BSP
- `gc9a01.py` kept only as backup/experimental

✅ **Test Files Ready:**
- `test_display.py` - Display-only test
- `test_complete.py` - Display + WiFi test

## Quick Test (Do This Now!)

### 1. Flash Firmware (if not done)
```bash
# Firmware is at:
/home/openclaw/.openclaw/workspace/magic-orb/firmware.uf2
```

1. Hold BOOT on RP2350
2. Connect USB
3. Release BOOT
4. Copy firmware.uf2 to the drive

### 2. Test Display

Copy `test_display.py` to your device and run it.

**Expected:**
- Screen fills with colors (red, green, blue, white, black)
- Shows "Magic Orb Ready!" text
- Draws concentric circles

**If it fails:**
- Confirm `hardware_profile.py` is copied to device root and matches this profile
- Tell me what error you get

### 3. Test WiFi + Display

Edit `test_complete.py` with your WiFi credentials, then run it.

**Expected:**
- Display test passes
- ESP32 responds to AT commands
- WiFi connects to your network
- Shows IP address on screen

## Pin Configuration

Source of truth: `hardware_profile.py` (**single tested profile only**).

```python
BOARD_NAME = "Waveshare RP2350-Touch-LCD-1.85C"
DISPLAY_CONTROLLER = "ST77916"
DISPLAY_BUS_TYPE = "QSPI"
DISPLAY_DRIVER = "lib/st77916.py"
BACKUP_DISPLAY_DRIVER = "lib/gc9a01.py"

LCD_SCLK = 10
LCD_D0   = 11
LCD_D1   = 12
LCD_D2   = 13
LCD_D3   = 14
LCD_CS   = 15
LCD_RST  = 16
LCD_TE   = 17
LCD_BL   = 24

ESP_TX   = 0  # GP0 -> ESP32 RX
ESP_RX   = 1  # GP1 <- ESP32 TX
ESP_UART_ID = 0
ESP_UART_BAUDRATE = 115200
```

## What to Tell Me

1. **Did display light up?**
2. **What colors showed?**
3. **Did WiFi connect?**
4. **Any error messages?**

This repo currently supports one tested board profile for Phase 0.

## Files in `/workspace/magic-orb/`

```
lib/
  ├── gc9a01.py      ← NEW: Round display driver
  ├── wifi_at.py     ← ESP-AT WiFi driver
  └── display.py     ← UI helpers

test_display.py      ← Test display only
test_complete.py     ← Test display + WiFi
firmware.uf2         ← MicroPython firmware
```

## Next After Testing

Once hardware is confirmed working:
1. Create `secrets.py` with config
2. Build PTT interface
3. Connect to OpenClaw

---

*Status as of 2026-02-10 12:40 UTC*
