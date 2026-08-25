import json
import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer


def parse_mac(value: str) -> bytes:
    cleaned = value.replace(":", "").replace("-", "").replace(" ", "")
    if len(cleaned) != 12:
        raise ValueError("BDP_MAC must contain 12 hexadecimal characters")
    return bytes.fromhex(cleaned)


BDP_MAC = parse_mac(os.environ["BDP_MAC"])
BROADCAST = os.environ.get("LAN_BROADCAST", "255.255.255.255")
WOL_PORT = int(os.environ.get("WOL_PORT", "8090"))
MAGIC_PACKET_PORT = int(os.environ.get("MAGIC_PACKET_PORT", "9"))


def send_wol() -> None:
    packet = b"\xff" * 6 + BDP_MAC * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (BROADCAST, MAGIC_PACKET_PORT))


class Handler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"ok": True})
        else:
            self._json(404, {"ok": False, "error": "Not found"})

    def do_POST(self):
        if self.path != "/wake":
            self._json(404, {"ok": False, "error": "Not found"})
            return
        try:
            send_wol()
            self._json(200, {"ok": True})
        except Exception as exc:
            self._json(500, {"ok": False, "error": str(exc)})

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")


HTTPServer(("0.0.0.0", WOL_PORT), Handler).serve_forever()
