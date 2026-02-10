# Magic Orb - Development Roadmap

## Vision
A portable, round-display voice node for OpenClaw + Home Assistant. Think of it as a "magic orb" you can carry around the house - tap to talk, glance for info, control your world.

---

## Hardware Specs
- **MCU:** RP2350 (dual-core ARM/RISC-V, 150MHz)
- **Display:** 1.85" round touchscreen (360x360, ST77916 via QSPI)
- **Audio:** Built-in mic + speaker (BOX version)
- **WiFi:** ESP32-WROOM via UART (ESP-AT firmware)
- **Power:** 3.7V battery (portable)

---

## Phase 0: Foundation (Current)
**Goal:** Get hardware working

### Status
- [x] Hardware confirmed working (Waveshare C demo)
- [x] Pin configuration identified
- [ ] MicroPython QSPI driver (needs debugging)
- [ ] WiFi via ESP-AT tested

### Questions to Answer
- Can we get QSPI working in MicroPython, or should we use C?
- How reliable is ESP-AT for WiFi?

---


## Stabilization gate (before Phase 1)

Phase 1 work (PTT/audio/touch) is blocked until the stabilization shell (`app_stable.py`) has completed a continuous soak run for a target duration.

Suggested acceptance target:
- minimum 24h continuous runtime,
- no unrecovered WiFi disconnects,
- heartbeat continues throughout run,
- optional HTTP ping remains healthy when configured.

## Phase 1: PTT Widget
**Goal:** Basic push-to-talk voice interface

### Core Features
- [ ] Touch-based PTT (tap screen to talk)
- [ ] Record audio (max 10s)
- [ ] Send to OpenClaw gateway via HTTP
- [ ] Play TTS response on speaker
- [ ] Status display (idle, listening, thinking, speaking)

### UI States
```
┌─────────────┐
│   ◉ TAP     │  ← Idle (blue)
│  TO TALK    │
└─────────────┘

┌─────────────┐
│      ●      │  ← Recording (red pulsing)
│  LISTENING  │
└─────────────┘

┌─────────────┐
│   ◉ ◉ ◉     │  ← Thinking (orange)
│  Thinking   │
└─────────────┘
```

---

## Phase 2: Wake Word
**Goal:** Hands-free activation

### Implementation
- [ ] Evaluate Porcupine on RP2350
- [ ] Add wake word detection loop
- [ ] Visual feedback when wake word triggers
- [ ] Timeout if no speech detected

---

## Phase 3: Home Assistant Dashboard
**Goal:** Useful round display when not talking

### Tailored to Your Setup

**Main View - Clock + Status**
```
┌─────────────┐
│    10:42    │
│   ☀️ 72°F   │  ← Weather from HA
│   ┌─────┐   │
│   │ 🏠  │   │  ← Home status icon
│   └─────┘   │
│  WiFi ✓ 85% │  ← Battery + connection
└─────────────┘
```

**Quick Controls (swipe right)**
- Light toggles
- Volume
- Scene buttons

**Meshtastic Mesh View (swipe left)**
- Node positions
- Message count
- Signal strength

**OpenClaw Status (swipe up)**
- Online status
- Model info
- Uptime

### HA Entities to Display
- **Weather:** `weather.home`
- **Lights:** Quick toggle for common rooms
- **Sensors:** Temperature, humidity, air quality
- **Meshtastic:** Node count, last message
- **System:** OpenClaw status, battery level

---

## Phase 4: Advanced Features (Future)

### Voice-Activated Scenes
- "Hey Nova, movie mode" → dims lights, closes blinds
- "Goodnight" → bedtime routine
- "I'm leaving" → away mode

### Mesh Integration
- Receive Meshtastic messages on display
- Send quick preset messages
- Node map visualization

### Presence Detection
- Detect when orb moves (accelerometer if available)
- Room tracking via WiFi RSSI?
- Follow-me automation (lights follow orb)

---

## Open Questions

### Technical
1. **QSPI in MicroPython** - Can we make it work, or stick with C?
2. **Audio quality** - How good is the built-in mic/speaker?
3. **Battery life** - How long can it run?
4. **Memory** - How much RAM available after display driver?

### UX
1. **Touch responsiveness** - Multi-touch support?
2. **Charging** - USB-C passthrough while in use?

---

## Success Metrics

**Phase 1 (PTT)**
- [ ] Can ask "What time is it?" and hear response
- [ ] Response latency < 5 seconds
- [ ] Works from anywhere on WiFi

**Phase 2 (Wake Word)**
- [ ] "Hey Nova" triggers from 2m away
- [ ] False positive rate < 1/hour

**Phase 3 (HA Dashboard)**
- [ ] Can toggle lights from orb
- [ ] Weather displays correctly
- [ ] Battery lasts 6+ hours

---

## Resources

### Firmware & Demos
- Waveshare RP2350 MicroPython: https://files.waveshare.com/wiki/common/WAVESHARE-RP2350-20250711-v1.26.0.zip
- Waveshare Demo Code: https://files.waveshare.com/wiki/RP2350-Touch-LCD-1.85C/RP2350-Touch-LCD-1.85C-Demo.zip

### Libraries
- **ESP-AT:** lib/wifi_at.py
- **Display helpers:** lib/display.py
- **ST77916 driver:** lib/st77916.py (needs work)
- **Porcupine Wake Word:** https://picovoice.ai/platform/porcupine/

### Your Setup
- **OpenClaw Gateway:** http://192.168.1.239:18789
- **Home Assistant:** http://192.168.1.xxx:8123
- **Meshtastic:** Via socat on tonythecrab (192.168.1.244:4403)

---

*Last updated: 2026-02-10*
