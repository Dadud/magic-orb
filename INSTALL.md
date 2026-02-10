# 🔮 Magic Orb - Phase 0 Install (MicroPython)

This guide is intentionally scoped to the **selected Phase 0 runtime: MicroPython**.

## 1) Flash MicroPython firmware

1. Hold **BOOT** on the RP2350 board.
2. Connect USB-C.
3. Release **BOOT** when mass storage appears.
4. Copy `firmware/firmware.uf2` to the board drive.
5. Wait for auto reboot.

## 2) Connect with Thonny

1. Open Thonny.
2. Interpreter: **MicroPython (Raspberry Pi Pico / RP2)**.
3. Select the board COM/serial port.
4. Confirm REPL prompt appears.

## 3) Copy the canonical Phase 0 files

On device, create `/lib` and copy:
- `main.py` -> device root
- `lib/gc9a01.py` -> device `/lib/gc9a01.py`

> Phase 0 stabilization path uses only the files above for boot.

## 4) Reboot and verify boot status

- Reset board (or power cycle).
- Expect status output on the display indicating:
  - display init OK
  - ESP-AT UART init OK

## Optional: copy canonical staged test files

- `test_display.py` (Stage A: display-only)
- `test_esp_at_uart.py` (Stage B: ESP-AT UART-only)
- `test_complete.py` (Stage C: display + WiFi HTTP)

Run order is mandatory: Stage A -> Stage B -> Stage C.
Details and expected-output checklists are in `TESTING.md`.

Legacy scripts (`quick_test.py`, `simple_test.py`, `all_in_one_test.py`) are reference-only and not part of acceptance testing.

## Troubleshooting

### No REPL connection
- Re-select correct serial port in Thonny.
- Reflash `firmware/firmware.uf2`.

### Display does not update
- Verify MicroPython files were copied to correct paths.
- Re-check pin mapping in `main.py` / `test_display.py`.

### ESP-AT not responding
- Verify wiring:
  - RP2350 GP0 -> ESP32 RX
  - RP2350 GP1 <- ESP32 TX
- Confirm ESP32 has ESP-AT firmware.
