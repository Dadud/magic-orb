#!/usr/bin/env python3
"""
Magic Orb - RP2350 Voice Node for OpenClaw
Main CircuitPython entry point
"""
import time
import board
import digitalio
import audiobusio
import audiocore
import busio
from displayio import release_displays

# Local libs (copy to CIRCUITPY/lib/)
from lib.wifi_at import ESPATWiFi
from lib.display import RoundDisplay

# Import secrets (create from secrets.py.example)
try:
    from secrets import SECRETS
except ImportError:
    print("Create secrets.py from secrets.py.example!")
    while True:
        pass

# Hardware setup
print("Magic Orb starting...")

# Display
import displayio
import framebufferio
import rgbimg

# For Waveshare RP2350-Touch-LCD-1.85C
# Display is typically on SPI + some control pins
# Need to check Waveshare's library for exact pinout
# For now, placeholder:
try:
    display = board.DISPLAY  # If CircuitPython has built-in support
except:
    # Manual init would go here
    print("Display init needed - check Waveshare examples")
    display = None

# ESP-AT WiFi on UART
# ESP32 TX -> RP2350 RX (GP1/UART0 RX)
# ESP32 RX -> RP2350 TX (GP0/UART0 TX)
esp_tx = board.GP0
esp_rx = board.GP1
wifi = ESPATWiFi(esp_tx, esp_rx, debug=True)

# Audio (placeholder - need to check hardware config)
# Mic could be I2S, PDM, or analog
# Speaker likely I2S DAC
mic = None
speaker = None

# Touch (for PTT)
# The round display has touch - need to check library
touch = None

# Display helper
if display:
    ui = RoundDisplay(display)
    ui.wifi_status(False)
else:
    ui = None

# State machine
STATE_IDLE = 0
STATE_RECORDING = 1
STATE_SENDING = 2
STATE_THINKING = 3
STATE_PLAYING = 4

state = STATE_IDLE
audio_buffer = None

def connect_wifi():
    """Connect to WiFi via ESP-AT."""
    if ui:
        ui.text_center("Connecting WiFi...", scale=2)
    
    print(f"Connecting to {SECRETS['wifi_ssid']}...")
    success = wifi.connect(SECRETS['wifi_ssid'], SECRETS['wifi_password'])
    
    if ui:
        ui.wifi_status(success)
    
    return success

def record_audio(max_seconds: int = 10) -> bytes:
    """Record audio from mic. Returns WAV data."""
    # TODO: Implement based on actual mic hardware
    # For testing, return placeholder
    print("Recording...")
    time.sleep(2)  # Simulate recording
    return b"PLACEHOLDER_AUDIO_DATA"

def send_to_openclaw(audio_data: bytes) -> dict:
    """Send audio to OpenClaw gateway, get response."""
    url = f"{SECRETS['gateway_url']}/v1/audio/inference"
    headers = {
        "Authorization": f"Bearer {SECRETS['gateway_token']}"
    }
    
    status, body = wifi.http_post(
        url,
        data=audio_data,
        content_type="audio/wav",
        headers=headers
    )
    
    if status == 200:
        # Response should include TTS audio URL or data
        return {"success": True, "response": body}
    else:
        return {"success": False, "error": f"HTTP {status}"}

def play_audio(audio_data: bytes):
    """Play audio on speaker."""
    # TODO: Implement based on actual speaker hardware
    print("Playing response...")
    time.sleep(2)  # Simulate playback

def check_ptt() -> bool:
    """Check if PTT is being held (touch or button)."""
    # TODO: Implement touch detection
    # For now, placeholder
    return False

def main():
    global state, audio_buffer
    
    print("Magic Orb ready!")
    
    if ui:
        ui.ptt_button(active=False)
    
    while True:
        if state == STATE_IDLE:
            # Check for PTT
            if check_ptt():
                state = STATE_RECORDING
                audio_buffer = b""
                if ui:
                    ui.ptt_button(active=True)
                print("Recording started")
        
        elif state == STATE_RECORDING:
            # Recording - check for PTT release
            if not check_ptt():
                # PTT released, stop recording and send
                state = STATE_SENDING
                if ui:
                    ui.thinking()
                print("Recording stopped, sending...")
                
                # Actually send the audio
                result = send_to_openclaw(audio_buffer or b"test")
                
                if result["success"]:
                    state = STATE_PLAYING
                    if ui:
                        ui.playing()
                    play_audio(b"")  # Would pass actual audio
                else:
                    if ui:
                        ui.error(result.get("error", "Failed"))
                    time.sleep(2)
                    state = STATE_IDLE
                    if ui:
                        ui.ptt_button(active=False)
            else:
                # Still recording
                if mic:
                    # Would read audio samples here
                    pass
        
        elif state == STATE_PLAYING:
            # Wait for playback to finish
            # For now, just timeout
            time.sleep(3)
            state = STATE_IDLE
            if ui:
                ui.ptt_button(active=False)
        
        time.sleep(0.05)

# Run on boot
if __name__ == "__main__":
    connect_wifi()
    main()
