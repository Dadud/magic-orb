# Magic Orb 🔮

A portable, round-display voice node for OpenClaw + Home Assistant.

## Runtime decision (Phase 0)

**Selected target runtime: MicroPython.**

### In scope for stabilization
- Boot with a **single canonical entrypoint**: `main.py`
- Initialize display
- Initialize ESP-AT UART link
- Show on-device status
- Keep a 3-stage MicroPython validation path:
  - Stage A: `test_display.py` (display-only)
  - Stage B: `test_esp_at_uart.py` (ESP-AT UART-only)
  - Stage C: `test_complete.py` (combined display + WiFi HTTP)
- Require Stage A + Stage B pass before Stage C

### Deferred (kept, but not stabilized in Phase 0)
- CircuitPython runtime path (`code.py`, `code_minimal.py`, `lib/display.py`, `lib/wifi_at.py`) is now **experimental / reference-only**
- Legacy/alternative display drivers (for example `lib/gc9a01.py`) are retained for reference but are not part of the canonical Phase 0 boot path
- Phase 1 features (PTT/audio/touch) are explicitly deferred behind stabilization soak criteria

## CircuitPython stabilization shell (experimental)

For CircuitPython bring-up/reference work, use `code.py` -> `app_stable.py`.

`app_stable.py` intentionally includes only:
- boot banner,
- explicit state transitions (`BOOT -> DISPLAY_OK -> WIFI_OK -> HTTP_OK`),
- heartbeat logs,
- WiFi connect/reconnect watchdog checks,
- optional HTTP ping (`SECRETS["ping_url"]`).

Deferred placeholders for Phase 1 features are isolated in `app_future.py`.

### Soak gate before Phase 1

Phase 1 feature work can begin only after the stabilization shell runs continuously for a target soak duration (recommended minimum: **24 hours** with no unrecovered WiFi/display lockups).

## Hardware

- **Waveshare RP2350-Touch-LCD-1.85C** - Round 360x360 touchscreen
- **ESP32-WROOM** - WiFi via ESP-AT (UART)
- **Built-in:** Mic, speaker, 3.7V battery (BOX version)
- **Touch controller:** CST816
- **Audio codec:** ES8311

## Canonical Phase 0 boot path

1. Flash `firmware/firmware.uf2` (MicroPython).
2. Copy these files to the board:
   - `main.py` (root)
   - `lib/st77916.py` (`/lib`)
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
  TX = GP26 -> ESP32 RX
  RX = GP27 <- ESP32 TX
```


## Phase 0 validation order

1. Run **Stage A** (`test_display.py`).
2. Run **Stage B** (`test_esp_at_uart.py`).
3. Run **Stage C** (`test_complete.py`) only after A and B pass.

Failure signatures are documented in `TESTING.md` and mirrored in script banners for operator clarity.

## Phase 0 exit report

- Latest report: [`docs/phase0-exit.md`](docs/phase0-exit.md)

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
│   ├── st77916.py      # Canonical MicroPython ST77916 display driver
│   ├── gc9a01.py       # Legacy reference driver (non-canonical)
│   ├── wifi_at.py      # Experimental CircuitPython ESP-AT path
│   └── display.py      # Experimental CircuitPython UI helpers
├── test_display.py     # Stage A canonical test (display-only)
├── test_esp_at_uart.py # Stage B canonical test (ESP-AT UART-only)
├── test_complete.py    # Stage C canonical test (display + WiFi HTTP)
├── quick_test.py       # Legacy reference only (not acceptance)
├── simple_test.py      # Legacy reference only (not acceptance)
└── all_in_one_test.py  # Legacy reference only (not acceptance)
```

## Resources

- [Waveshare Wiki](https://www.waveshare.com/wiki/RP2350-Touch-LCD-1.85C)
- [Waveshare Demo Code](https://files.waveshare.com/wiki/RP2350-Touch-LCD-1.85C/RP2350-Touch-LCD-1.85C-Demo.zip)
- [OpenClaw Docs](https://docs.openclaw.ai)
