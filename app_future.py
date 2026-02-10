# EXPERIMENTAL (NON-TARGET RUNTIME): Deferred Phase 1 feature placeholders.
"""Deferred Phase 1 (PTT/audio/touch) placeholders.

Do not include these in stabilization acceptance.
These functions are intentionally non-functional until stabilization soak completes.
"""

import time


STATE_IDLE = 0
STATE_RECORDING = 1
STATE_SENDING = 2
STATE_THINKING = 3
STATE_PLAYING = 4


def record_audio(max_seconds=10):
    """Deferred: record audio from mic, return WAV bytes."""
    print("[DEFERRED] record_audio not implemented")
    time.sleep(min(1, max_seconds))
    return b"PLACEHOLDER_AUDIO_DATA"


def send_to_openclaw(_wifi, _secrets, _audio_data):
    """Deferred: upload audio to gateway and return response payload."""
    print("[DEFERRED] send_to_openclaw not implemented")
    return {"success": False, "error": "Deferred in stabilization phase"}


def play_audio(_audio_data):
    """Deferred: play TTS/response audio on speaker hardware."""
    print("[DEFERRED] play_audio not implemented")


def check_ptt(_touch=None):
    """Deferred: touch/button push-to-talk detection."""
    return False
