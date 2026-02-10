import importlib.util
import pathlib
import sys
import types
import unittest


class _DummyUART:
    def __init__(self, *args, **kwargs):
        pass


def _load_wifi_module():
    sys.modules.setdefault("busio", types.SimpleNamespace(UART=_DummyUART))
    module_path = pathlib.Path(__file__).resolve().parents[1] / "lib" / "wifi_at.py"
    spec = importlib.util.spec_from_file_location("wifi_at", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


wifi_at = _load_wifi_module()
ESPATWiFi = wifi_at.ESPATWiFi


class ParseResponseTests(unittest.TestCase):
    def test_parses_echo_intermediate_and_ok_status(self):
        raw = 'AT+CWMODE=1\r\n\r\nno change\r\n\r\nOK\r\n'
        parsed = ESPATWiFi.parse_response(raw, command="AT+CWMODE=1")

        self.assertEqual(parsed["echo"], "AT+CWMODE=1")
        self.assertEqual(parsed["status"], "OK")
        self.assertEqual(parsed["intermediate"], ["no change"])
        self.assertEqual(parsed["payload"], "")

    def test_parses_error_status_and_retains_details(self):
        raw = 'AT+CWJAP="bad","pw"\r\n\r\nWIFI DISCONNECT\r\nFAIL\r\n\r\nERROR\r\n'
        parsed = ESPATWiFi.parse_response(raw, command='AT+CWJAP="bad","pw"')

        self.assertEqual(parsed["status"], "ERROR")
        self.assertIn("WIFI DISCONNECT", parsed["intermediate"])
        self.assertIn("FAIL", parsed["intermediate"])

    def test_extracts_ipd_payload(self):
        raw = (
            "Recv 47 bytes\r\n"
            "+IPD,43:HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nhello\r\n"
            "CLOSED\r\n"
        )
        parsed = ESPATWiFi.parse_response(raw)

        self.assertTrue(parsed["payload"].startswith("HTTP/1.1 200 OK"))
        self.assertIn("hello", parsed["payload"])

    def test_extracts_http_payload_without_ipd(self):
        raw = "HTTP/1.1 204 No Content\r\nDate: today\r\n\r\n"
        parsed = ESPATWiFi.parse_response(raw)

        self.assertEqual(parsed["payload"], "")
        self.assertIsNone(parsed["status"])


if __name__ == "__main__":
    unittest.main()
