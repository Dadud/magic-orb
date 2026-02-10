# Phase 0 Exit Report (Frozen Runtime/Hardware Profile)

Date (UTC): 2026-02-10T14:33:51Z

## 1) Board revision + firmware/runtime version

- Board profile (frozen): `Waveshare RP2350-Touch-LCD-1.85C` (from `hardware_profile.py`).
- Board peripherals recorded in profile: touch controller `CST816`, audio codec `ES8311`.
- ESP-AT UART wiring (frozen profile): TX=GP26, RX=GP27.
- Board revision: **not exposed in repository metadata** (no explicit rev field in profile/docs).
- Firmware artifact inspected: `firmware/firmware.uf2`.
- Runtime string extracted from UF2:
  - `MicroPython v1.26.0-preview.265.ge57aa7e70.dirty on 2025-07-11`
  - `MicroPython-1.26.0-preview-arm--with-newlib3.3.0`

Command used:

```bash
strings firmware/firmware.uf2 | rg -n -m 5 "MicroPython|RP2350|v[0-9]+\.[0-9]+"
```

## 2) Stage A/B/C pass-fail with timestamps

> Execution environment limitation: this container is standard CPython/Linux and does not provide a connected RP2350 device, MicroPython runtime, or `machine` module.

| Stage | Canonical script | Timestamp (UTC) | Result | Notes |
|---|---|---|---|---|
| A | `test_display.py` | 2026-02-10T14:32:00Z | **FAIL (environment)** | `ModuleNotFoundError: No module named 'st77916'` because script appends `/lib` (MicroPython board FS path), unavailable in host CPython. |
| B | `test_esp_at_uart.py` | 2026-02-10T14:32:22Z | **FAIL (environment)** | `ModuleNotFoundError: No module named 'machine'` (MicroPython-only module). |
| C | `test_complete.py` | 2026-02-10T14:32:22Z | **NOT RUN** | Blocked by Stage A/B gate and missing board runtime. |

Commands used:

```bash
python test_display.py
python test_esp_at_uart.py
```

## 3) WiFi connect timing (>=10 cycles)

- **Status:** Not measurable in this environment (no ESP-AT UART device present).
- Required metric (median/worst across >=10 cycles): **N/A (blocked)**.

## 4) HTTP success rate (>=50 requests)

- **Status:** Not measurable via canonical Stage C path in this environment (depends on ESP-AT over UART on board).
- Required metric (success rate across >=50 requests): **N/A (blocked)**.

## 5) Soak result (target duration, resets, memory drift)

- **Status:** Not executable in this container for the MicroPython board runtime.
- Target duration: recommended 24h soak (per `TESTING.md`).
- Resets observed: **N/A (blocked)**.
- Memory drift notes: **N/A (blocked)**.

## Repro steps on actual hardware (to complete this report)

1. Flash `firmware/firmware.uf2` to RP2350 board.
2. Copy canonical test scripts/files to board per `TESTING.md`.
3. Run Stage A -> Stage B -> Stage C in order, capturing serial logs with timestamps.
4. Run scripted Stage C loop for:
   - >=10 WiFi connect cycles (compute median + worst-case connect time)
   - >=50 HTTP requests (compute success rate)
5. Run 24h soak and record reboot count + periodic free-memory samples.

