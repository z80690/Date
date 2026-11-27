#!/usr/bin/env python3
"""
把 GitHub 靶机 synology-oauth-lab 的漏洞函数包成 HTTP 服务。
只绑 127.0.0.1，不碰外网。供 ARTEX 当靶子。
"""
import sys
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, r"D:\refs\synology-oauth-lab")
from lab.vulnerable_server import VulnerableOAuthServer

S = VulnerableOAuthServer()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/oauth/demo"):
            r = S.vulnerable_redirect({"client_id": "demo_client", "state": "x"})
            self._send(200, {
                "cve": r["cve_reference"],
                "vulnerability": r["vulnerability"],
                "location": r["headers"]["Location"],
            })
        elif self.path == "/health":
            self._send(200, {"status": "ok"})
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, fmt, *args):
        print("[target]", fmt % args, flush=True)


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 9099), Handler).serve_forever()
