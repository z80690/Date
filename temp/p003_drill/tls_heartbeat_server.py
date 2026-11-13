"""Local HTTPS target endpoint (stand-in for DVWA until it is deployed).

Binds 127.0.0.1:8443 only. Serves a deterministic JSON health payload so the
disguise drill has a real TLS endpoint on the loopback whitelist (W1).
"""

import json
import ssl
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HOST, PORT = "127.0.0.1", 8443
CERT_DIR = Path(__file__).resolve().parent / "certs"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(
            {"status": "ok", "service": "p003-https-target", "note": "DVWA stand-in"}
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("[tls-target]", fmt % args, flush=True)


if __name__ == "__main__":
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(
        str(CERT_DIR / "cert.pem"),
        str(CERT_DIR / "key.pem"),
    )
    server = HTTPServer((HOST, PORT), Handler)
    server.socket = ctx.wrap_socket(server.socket, server_side=True)
    print(f"[tls-target] listening on https://{HOST}:{PORT} (loopback only)", flush=True)
    server.serve_forever()