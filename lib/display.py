# EXPERIMENTAL (NON-TARGET RUNTIME): CircuitPython display helpers kept for reference only.
# Display utilities for round 360x360 LCD
import displayio
import terminalio
from adafruit_display_text import label
import math

# Screen center and radius
CENTER_X = 180
CENTER_Y = 180
RADIUS = 170

class RoundDisplay:
    """Helper for round display UI elements."""
    
    def __init__(self, display):
        self.display = display
        self.splash = displayio.Group()
        display.show(self.splash)
        
    def clear(self):
        """Clear all elements."""
        while len(self.splash) > 0:
            self.splash.pop()
    
    def text_center(self, text: str, y_offset: int = 0, scale: int = 2, color: int = 0xFFFFFF):
        """Draw centered text."""
        text_area = label.Label(terminalio.FONT, text=text, scale=scale, color=color)
        text_area.anchor_point = (0.5, 0.5)
        text_area.anchored_position = (CENTER_X, CENTER_Y + y_offset)
        self.splash.append(text_area)
        return text_area
    
    def status_ring(self, color: int = 0x00FF00, progress: float = 1.0):
        """Draw a status ring around the edge."""
        # For now, just a simple colored circle background
        # Full ring graphics would need vectorio or bitmap
        pass
    
    def ptt_button(self, active: bool = False):
        """Draw PTT button state."""
        self.clear()
        
        if active:
            # Recording - red center with pulsing effect
            self.text_center("● LISTENING", y_offset=0, scale=3, color=0xFF0000)
            self.text_center("Release to send", y_offset=50, scale=1, color=0x888888)
        else:
            # Idle - tap to talk
            self.text_center("◉ TAP TO TALK", y_offset=0, scale=2, color=0x00AAFF)
            self.text_center("Magic Orb", y_offset=-60, scale=1, color=0x666666)
    
    def thinking(self):
        """Show thinking animation."""
        self.clear()
        self.text_center("◉ ◉ ◉", y_offset=0, scale=3, color=0xFFAA00)
        self.text_center("Thinking...", y_offset=50, scale=1, color=0x888888)
    
    def playing(self):
        """Show playing response."""
        self.clear()
        self.text_center("♪ ♪ ♪", y_offset=0, scale=3, color=0x00FF00)
        self.text_center("Speaking...", y_offset=50, scale=1, color=0x888888)
    
    def error(self, message: str = "Error"):
        """Show error state."""
        self.clear()
        self.text_center("✗", y_offset=-20, scale=4, color=0xFF4444)
        self.text_center(message, y_offset=40, scale=1, color=0xFF4444)
    
    def wifi_status(self, connected: bool):
        """Show WiFi status indicator."""
        color = 0x00FF00 if connected else 0xFF0000
        text = "WiFi ✓" if connected else "WiFi ✗"
        indicator = label.Label(terminalio.FONT, text=text, scale=1, color=color)
        indicator.anchor_point = (0, 0)
        indicator.anchored_position = (10, 10)
        self.splash.append(indicator)
