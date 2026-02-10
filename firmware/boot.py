"""Boot script for the clean RP2350-Touch-LCD-1.85C MicroPython base.

Purpose:
- Keep boot deterministic
- Ensure local modules are importable from /drivers and /board
"""
import os
import sys

for path in ("/drivers", "/board"):
    if path not in sys.path:
        sys.path.append(path)

print("[boot] RP2350 Touch LCD 1.85C firmware boot.py loaded")
print("[boot] cwd:", os.getcwd())
