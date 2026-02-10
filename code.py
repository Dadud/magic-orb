# EXPERIMENTAL (NON-TARGET RUNTIME): CircuitPython prototype kept for reference only.
"""CircuitPython entrypoint for the stabilization shell.

This file now runs app_stable.py only.
Deferred Phase 1 placeholders live in app_future.py.
"""

from app_stable import main


if __name__ == "__main__":
    main()
