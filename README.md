# Magic Orb 🔮

A portable, round-display voice node for OpenClaw + Home Assistant.

## Runtime decision (Phase 0)

**Selected target runtime: MicroPython.**

### In scope for stabilization
- Boot with a **single canonical entrypoint**: `main.py`
- Initialize display
- Initialize ESP-AT UART link
- Show on-device status
- Keep MicroPython test path (`test_display.py`, `test_complete.py`) as the active validation workflow

### Deferred (kept, but not stabilized in Phase 0)
- CircuitPython runtime path (`code.py`, `code_minimal.py`, `lib/display.py`, `lib/wifi_at.py`) is now **experimental / reference-only**
- Alternative display/runtime experiments (for example `lib/st77916.py`) remain in repo but are not part of the Phase 0 boot path

## Hardware

- **Waveshare RP2350-Touch-LCD-1.85C** - Round 360x360 touchscreen
- **ESP32-WROOM** - WiFi via ESP-AT (UART)
- **Built-in:** Mic, speaker, 3.7V battery (BOX version)

## Canonical Phase 0 boot path

1. Flash `firmware/firmware.uf2` (MicroPython).
2. Copy these files to the board:
   - `main.py` (root)
   - `lib/gc9a01.py` (`/lib`)
3. Reboot.

`main.py` intentionally does only:
- display init,
- ESP-AT UART init,
- status rendering.

## Pin Configuration (current MicroPython baseline)

```text
Display:
  LCD_DC   = GP8
  LCD_CS   = GP9
  LCD_SCK  = GP10
  LCD_MOSI = GP11
  LCD_MISO = GP12
  LCD_BL   = GP13
  LCD_RST  = GP15

ESP32 (UART0):
  TX = GP0  -> ESP32 RX
  RX = GP1  <- ESP32 TX
```

## Project Structure

```text
magic-orb/
├── main.py             # Canonical MicroPython Phase 0 entrypoint
├── README.md
├── INSTALL.md
├── TESTING.md
├── firmware/
│   └── firmware.uf2    # MicroPython firmware
├── lib/
│   ├── gc9a01.py       # MicroPython display driver
│   ├── st77916.py      # Experimental display/runtime path
│   ├── wifi_at.py      # Experimental CircuitPython ESP-AT path
│   └── display.py      # Experimental CircuitPython UI helpers
├── test_display.py     # MicroPython display test
└── test_complete.py    # MicroPython display + WiFi test
```

## Resources

- [Waveshare Wiki](https://www.waveshare.com/wiki/RP2350-Touch-LCD-1.85C)
- [Waveshare Demo Code](https://files.waveshare.com/wiki/RP2350-Touch-LCD-1.85C/RP2350-Touch-LCD-1.85C-Demo.zip)
- [OpenClaw Docs](https://docs.openclaw.ai)
