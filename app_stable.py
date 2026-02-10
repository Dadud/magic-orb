# EXPERIMENTAL (NON-TARGET RUNTIME): CircuitPython stabilization shell for bring-up only.
"""Magic Orb CircuitPython stabilization shell.

Scope intentionally limited to:
- boot banner,
- display heartbeat,
- WiFi connect/reconnect,
- optional HTTP ping health check.

Deferred Phase 1 functionality (PTT/audio/touch) is moved to app_future.py.
"""

import time
import board

from lib.wifi_at import ESPATWiFi
from lib.display import RoundDisplay

try:
    from secrets import SECRETS  # type: ignore
except ImportError:
    SECRETS = {}

STATE_BOOT = "BOOT"
STATE_DISPLAY_OK = "DISPLAY_OK"
STATE_WIFI_OK = "WIFI_OK"
STATE_HTTP_OK = "HTTP_OK"

HEARTBEAT_INTERVAL_S = 5
WATCHDOG_INTERVAL_S = 15


def boot_banner():
    """Print a deterministic startup banner to serial."""
    print("=" * 50)
    print("Magic Orb | CircuitPython Stabilization Shell")
    print("Scope: banner + heartbeat + wifi + optional http ping")
    print("State path: BOOT -> DISPLAY_OK -> WIFI_OK -> HTTP_OK")
    print("=" * 50)


def create_ui():
    """Initialize display UI if board display is available."""
    try:
        display = board.DISPLAY
        return RoundDisplay(display)
    except Exception as exc:
        print("Display unavailable:", exc)
        return None


def show_state(ui, state, detail=""):
    """Render explicit stabilization state transitions on-screen."""
    print("STATE:", state, detail)
    if not ui:
        return

    ui.clear()
    ui.text_center("Magic Orb", y_offset=-85, scale=2, color=0x00AAFF)
    ui.text_center("BOOT -> DISPLAY_OK", y_offset=-35, scale=1, color=0x888888)
    ui.text_center("-> WIFI_OK -> HTTP_OK", y_offset=-15, scale=1, color=0x888888)
    ui.text_center(state, y_offset=20, scale=2, color=0x00FF66)
    if detail:
        ui.text_center(detail[:28], y_offset=58, scale=1, color=0xFFFFFF)


def create_wifi():
    return ESPATWiFi(board.GP0, board.GP1, debug="errors")


def wifi_connect_or_reconnect(wifi):
    """Connect or reconnect WiFi if credentials are provided."""
    ssid = SECRETS.get("wifi_ssid")
    password = SECRETS.get("wifi_password")
    if not ssid or not password:
        print("WiFi credentials missing in secrets.py (wifi_ssid/wifi_password)")
        return False

    if wifi.is_connected():
        return True

    print("WiFi not connected; attempting connect/reconnect...")
    return wifi.connect(ssid, password)


def optional_http_ping(wifi):
    """Optional HTTP ping check if ping_url is configured."""
    ping_url = SECRETS.get("ping_url")
    if not ping_url:
        print("HTTP ping skipped (set SECRETS['ping_url'] to enable)")
        return None

    print("HTTP ping:", ping_url)
    status, _body = wifi.http_get(ping_url)
    print("HTTP ping status:", status)
    return status


def main():
    boot_banner()

    ui = create_ui()
    show_state(ui, STATE_BOOT, "starting")

    if ui:
        show_state(ui, STATE_DISPLAY_OK, "display online")

    wifi = create_wifi()

    last_heartbeat = 0.0
    last_watchdog = 0.0

    while True:
        now = time.monotonic()

        if now - last_watchdog >= WATCHDOG_INTERVAL_S:
            last_watchdog = now
            wifi_ok = wifi_connect_or_reconnect(wifi)
            if wifi_ok:
                show_state(ui, STATE_WIFI_OK, "wifi connected")
                ping_status = optional_http_ping(wifi)
                if ping_status and 200 <= ping_status < 500:
                    show_state(ui, STATE_HTTP_OK, "http ping ok")
                elif ping_status is not None:
                    show_state(ui, STATE_WIFI_OK, "http ping failed")
            else:
                show_state(ui, STATE_DISPLAY_OK, "wifi reconnecting")

        if now - last_heartbeat >= HEARTBEAT_INTERVAL_S:
            last_heartbeat = now
            print("HEARTBEAT t={:.0f}s".format(now))

        time.sleep(0.1)


if __name__ == "__main__":
    main()
