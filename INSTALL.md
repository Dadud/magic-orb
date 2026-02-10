# 🔮 Magic Orb - Installation Steps

## Step 1: Get the Files

**Option A: From OpenClaw VM (you're on Windows)**
```bash
# In PowerShell or CMD:
scp openclaw@192.168.1.239:/home/openclaw/magic-orb.tar.gz .
tar -xzf magic-orb.tar.gz  # Or use 7-Zip to extract
```

**Option B: Direct copy from workspace**
Files are in: `\\192.168.1.239\home\openclaw\.openclaw\workspace\magic-orb\`

## Step 2: Flash Firmware

1. **Hold BOOT** button on RP2350 board
2. **Connect USB-C** to your computer
3. **Release BOOT** - a drive appears (RPI-RP2 or similar)
4. **Copy `firmware.uf2`** to that drive
5. Device reboots automatically (drive disappears)

## Step 3: Install Drivers (if needed)

After reboot, you should see a new COM port in Device Manager.
If not, install drivers: https://www.raspberrypi.com/documentation/microcontrollers/rp2040.html#driver-installation

## Step 4: Connect with Thonny

1. Download Thonny: https://thonny.org/
2. Open Thonny
3. Bottom-right corner → Select "MicroPython (Raspberry Pi Pico)"
4. Select the COM port for your RP2350
5. You should see `>>>` REPL prompt

## Step 5: Copy Files to Device

**In Thonny:**
1. View → Files
2. Navigate to `magic-orb/` folder on your computer (left side)
3. Create `lib` folder on the device (right side)
4. Copy these files:
   - `lib/st77916.py` → device `lib/`
   - `lib/wifi_at.py` → device `lib/`
   - `test_display.py` → device root

## Step 6: Test Display

**In Thonny:**
1. Open `test_display.py`
2. Edit pin config if needed (check your board version)
3. Click Run (F5)
4. **Expected:** Screen flashes colors, shows text

## Step 7: Test WiFi

1. Open `test_complete.py`
2. Edit WiFi credentials at the top:
   ```python
   WIFI_SSID = "YOUR_WIFI_NAME"
   WIFI_PASS = "YOUR_WIFI_PASSWORD"
   ```
3. Run it
4. **Expected:** Display + WiFi both pass

## Troubleshooting

**Display doesn't light up:**
- Check pin connections match your board
- Try the pre-built firmware from Waveshare: `RP2350-Touch-LCD-1.85C-Demo/C/firmware/lcd_touch.uf2`

**WiFi fails:**
- Check ESP32 wiring: TX→GP1, RX→GP0
- Verify ESP32 has ESP-AT firmware

**Can't connect to REPL:**
- Try different COM port
- Hold BOOT + press RESET, release RESET first
- Re-flash firmware

## Pin Reference

From Waveshare demo:
```
Display (QSPI):
  SCLK = GP10
  D0   = GP11
  D1   = GP12
  D2   = GP13
  D3   = GP14
  CS   = GP15
  RST  = GP16
  TE   = GP17
  BL   = GP24

ESP32 (UART):
  TX   = GP0  → ESP32 RX
  RX   = GP1  ← ESP32 TX
```

## What to Report

1. Did screen light up?
2. What did you see? (colors, text, nothing?)
3. Any error messages in Thonny shell?
4. Did WiFi connect?

---

*Good luck! 🔮*
