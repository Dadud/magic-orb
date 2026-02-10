# RP2350-Touch-LCD-1.85C Clean MicroPython Base

This folder is a clean, developer-oriented firmware baseline for the Waveshare **RP2350-Touch-LCD-1.85C**.

It is derived from the official Waveshare demo package and keeps only the required hardware setup for:
- ST77916 display bring-up
- CST816 touch bring-up
- Backlight control

## Directory layout

```text
firmware/
  board/
    pins.py
    config.py
  drivers/
    display.py
    touch.py
    backlight.py
  boot.py
  main.py
  README.md
```

## Hardware mapping source (official demo)

Pin and controller assignments were taken from Waveshare BSP headers in:
- `libraries/bsp/bsp_st77916.h`
- `libraries/bsp/bsp_i2c.h`
- `libraries/bsp/bsp_cst816.h`

### Display (ST77916)
- SCLK: GP10
- D0..D3: GP11..GP14
- CS: GP15
- RST: GP16
- TE: GP17
- BL: GP24
- Resolution: 360x360

### Touch (CST816)
- I2C1
- SDA: GP6
- SCL: GP7
- RST: GP9
- INT: GP8
- Address: `0x15`

## What works now

- Boots cleanly into `main.py`.
- Initializes ST77916 and renders text + shapes.
- Initializes CST816 and validates chip ID (`0x03`).
- Prints touch coordinates to USB REPL when touched.
- Uses non-blocking main loop cadence (`ticks_ms` based polling + short sleep).

## What does not yet exist in this base

- Gesture recognition/multi-touch abstraction (CST816 is used in single-point polling mode).
- UI framework integration (e.g., LVGL porting not included in this baseline).
- Audio, battery, RTC, or WiFi application logic.

## Flashing / deployment

### 1) Flash MicroPython UF2

1. Hold **BOOT** on the RP2350 board.
2. Plug USB.
3. Copy `firmware.uf2` (MicroPython UF2) to the mass-storage drive.
4. Board reboots to MicroPython.

### 2) Copy firmware files to the board filesystem

On the board, create these directories:
- `/board`
- `/drivers`

Copy files from this folder to the board root:
- `boot.py` -> `/boot.py`
- `main.py` -> `/main.py`
- `board/pins.py` -> `/board/pins.py`
- `board/config.py` -> `/board/config.py`
- `drivers/display.py` -> `/drivers/display.py`
- `drivers/touch.py` -> `/drivers/touch.py`
- `drivers/backlight.py` -> `/drivers/backlight.py`

### 3) Reset board

After reset, you should see startup graphics and REPL logs.

## Known-good validation checklist

- [ ] Display backlight turns on.
- [ ] Startup text and boxed UI are visible.
- [ ] Touching the panel prints `touch: x=..., y=...` in REPL.
- [ ] No exception traceback at boot.
- [ ] REPL is available over USB serial.

## Where to add app logic

- Keep hardware drivers in `drivers/`.
- Keep board constants in `board/`.
- Add your app state machine in `main.py` (or split into `app/` modules and import from `main.py`).

## How to extend this for LVGL later

- Keep `board/pins.py` and `board/config.py` as single source of truth.
- Replace `drivers/display.py` flush path with LVGL draw buffer callback.
- Replace `main.py` loop with LVGL tick/task handler loop.
- Keep `drivers/touch.py` as LVGL indev source.

## Assumptions and risk notes

1. The display init command table is ported from the Waveshare ST77916 BSP init path.  
   If Waveshare publishes a newer init sequence for this specific panel batch, update only the `init_cmds` table.
2. Touch controller is assumed CST816 at `0x15` with chip ID `0x03` as in Waveshare BSP.  
   If your board revision uses a different touch IC, replace only `drivers/touch.py` and keep the same app interface.
3. This baseline prioritizes deterministic bring-up and readability over max rendering throughput.
