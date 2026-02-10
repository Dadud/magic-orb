# Magic Orb 🔮

A portable, round-display voice node for OpenClaw + Home Assistant.

## Hardware

- **Waveshare RP2350-Touch-LCD-1.85C** - Round 360x360 touchscreen
- **ESP32-WROOM** - WiFi via ESP-AT (UART)
- **Built-in:** Mic, speaker, 3.7V battery (BOX version)

## Current Status

### ✅ What Works
- Hardware confirmed working (Waveshare C demo works)
- Display lights up and responds
- Basic pin configuration identified

### 🚧 In Progress
- MicroPython QSPI display driver (needs debugging)
- WiFi connection via ESP-AT
- PTT voice interface

### 📋 Planned
- Voice interface with OpenClaw
- "Hey Nova" wake word
- Home Assistant dashboard
- Meshtastic integration

## Architecture

```
┌─────────────────┐
│   RP2350        │
│  360x360 round  │    QSPI     ┌──────────┐
│   ST77916 LCD   │◄───────────►│ ESP32    │
│   + Touch       │    UART     │(ESP-AT)  │
│   Mic + Speaker │             └────┬─────┘
└─────────────────┘                  │ WiFi
                                     ▼
                              ┌──────────┐
                              │ OpenClaw │
                              │ Gateway  │
                              └──────────┘
```

## Pin Configuration

From Waveshare RP2350-Touch-LCD-1.85C demo:

**Display (QSPI):**
- SCLK = GP10
- D0-D3 = GP11-14 (4-bit data)
- CS = GP15
- RST = GP16
- TE = GP17
- BL = GP24

**ESP32 (UART0):**
- TX = GP0 → ESP32 RX
- RX = GP1 ← ESP32 TX

## Getting Started

### Option 1: Waveshare Demo (Working)
```bash
# Flash the working demo
firmware/lcd_touch.uf2
```

### Option 2: MicroPython (Experimental)
```bash
# Flash MicroPython
firmware/firmware.uf2

# Copy drivers
lib/st77916.py
lib/wifi_at.py
```

See [INSTALL.md](INSTALL.md) for detailed steps.

## Project Structure

```
magic-orb/
├── README.md           # This file
├── INSTALL.md          # Installation guide
├── ROADMAP.md          # Development plan
├── TESTING.md          # Test procedures
├── firmware/
│   ├── firmware.uf2        # MicroPython
│   └── lcd_touch.uf2       # Waveshare demo (working)
├── lib/
│   ├── st77916.py      # ST77916 QSPI driver
│   ├── wifi_at.py      # ESP-AT WiFi driver
│   └── display.py      # UI helpers
├── test_display.py     # Display test
├── test_complete.py    # Display + WiFi test
└── simple_test.py      # Basic GPIO test
```

## Next Steps

1. **Fix MicroPython QSPI driver** (or switch to C)
2. **Verify WiFi via ESP-AT**
3. **Implement PTT interface**
4. **Connect to OpenClaw gateway**
5. **Add wake word detection**
6. **Build HA dashboard**

## Resources

- [Waveshare Wiki](https://www.waveshare.com/wiki/RP2350-Touch-LCD-1.85C)
- [Waveshare Demo Code](https://files.waveshare.com/wiki/RP2350-Touch-LCD-1.85C/RP2350-Touch-LCD-1.85C-Demo.zip)
- [OpenClaw Docs](https://docs.openclaw.ai)

## License

TBD - Currently using Waveshare examples

---

*Project started: 2026-02-10*
*Status: Experimental - hardware confirmed, drivers in progress*
