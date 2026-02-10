# 🔮 Magic Orb - Phase 0 Testing (MicroPython)

This guide defines a strict 3-stage validation path for the selected stabilization runtime: **MicroPython**.

## Stage definitions (canonical)

- **Stage A — display-only**
  - Canonical script: `test_display.py`
  - Purpose: verify ST77916 init + basic rendering only.
- **Stage B — ESP-AT UART-only**
  - Canonical script: `test_esp_at_uart.py`
  - Purpose: verify UART link + AT command responsiveness only.
- **Stage C — combined display + WiFi HTTP**
  - Canonical script: `test_complete.py`
  - Purpose: verify integrated display + ESP-AT WiFi + HTTP status parsing.

> **Execution gate:** Stage A and Stage B must both PASS before running Stage C.

## Prerequisites

- `firmware/firmware.uf2` flashed.
- Device files copied:
  - `main.py`
  - `lib/gc9a01.py`
- For staged validation, also copy:
  - `test_display.py` (Stage A)
  - `test_esp_at_uart.py` (Stage B)
  - `test_complete.py` (Stage C)

---

## Stage A checklist (`test_display.py`)

Run from Thonny:

```python
import test_display
```

Expected output/behavior checklist:

- Banner shows `Stage A (Display-Only)`.
- Display initializes in <= 5000ms.
- Color sweep renders (RED, GREEN, BLUE, WHITE, BLACK).
- Text/geometry render without lockup.
- Terminal ends with `✓ Stage A PASS`.

Failure signatures:

- `display init timeout`
- Any exception during render loop

---

## Stage B checklist (`test_esp_at_uart.py`)

Run from Thonny:

```python
import test_esp_at_uart
```

Expected output/behavior checklist:

- Banner shows `Stage B (ESP-AT UART-Only)`.
- `AT` probe returns `OK`.
- `AT+GMR` returns `OK`.
- `AT+CWMODE=1` returns `OK`.
- Terminal ends with `✓ Stage B PASS`.

Failure signatures:

- `no AT response`
- firmware query failure
- station mode set failure

---

## Stage C checklist (`test_complete.py`)

> **Do not run Stage C unless Stage A and Stage B both passed in this session.**

Before run, edit credentials in file:

```python
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"
```

Run from Thonny:

```python
import test_complete
```

Expected output/behavior checklist:

- Banner shows `Stage C (Display + WiFi HTTP)`.
- Display initializes in <= 5000ms.
- `AT` probe succeeds.
- WiFi association succeeds (`OK` or `WIFI GOT IP`).
- HTTP transaction completes and status line is parsed.
- Terminal ends with `✓ Stage C PASS`.

Failure signatures:

- `display init timeout`
- `no AT response`
- `HTTP status parse fail`

---

## Canonical-vs-legacy note

To reduce operator confusion, only the three stage scripts above are primary validation artifacts.
Legacy exploratory scripts (`quick_test.py`, `simple_test.py`, `all_in_one_test.py`) are retained for reference only and are **not** part of acceptance testing.

## Current baseline pins (MicroPython tests)

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

ESP_TX   = 0
ESP_RX   = 1
```

## Deferred runtime note

CircuitPython files are kept in-repo for reference but are not part of Phase 0 stabilization or acceptance testing.
