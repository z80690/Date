"""服务器骨架（任务 2.13）。

回环绑定（禁默认监听外部网卡，4.3.6）、契约版本 v1（4.4.2）、
鉴权扩展点预留（本阶段空置可插入，4.3.8）。
标准库 http.server 实现，单机进程内（design D7）。
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, Optional

CONTRACT_VERSION = "v1"
BIND_HOST = "127.0.0.1"


class AuthPlugin:
    """鉴权扩展点：本阶段空置（恒通过），可插入自定义实现（4.3.8）。"""

    def check(self, headers: Any) -> bool:
        return True


class _Handler(BaseHTTPRequestHandler):
    dispatcher: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
    auth_plugin: AuthPlugin = AuthPlugin()

    def log_message(self, fmt: str, *args: Any) -> None:
        pass

    def _respond(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("X-Contract-Version", CONTRACT_VERSION)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if not self.auth_plugin.check(self.headers):
            self._respond({"error": "UNAUTHORIZED"}, 401)
            return
        fn = self.dispatcher.get(self.path)
        if not fn:
            self._respond({"error": "NOT_FOUND", "path": self.path, "contract_version": CONTRACT_VERSION}, 404)
            return
        try:
            self._respond(fn({}))
        except Exception as exc:
            self._respond({"error": type(exc).__name__, "message": str(exc)}, 400)

    def do_POST(self) -> None:
        if not self.auth_plugin.check(self.headers):
            self._respond({"error": "UNAUTHORIZED"}, 401)
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError:
            self._respond({"error": "BAD_JSON"}, 400)
            return
        fn = self.dispatcher.get(self.path)
        if not fn:
            self._respond({"error": "NOT_FOUND", "path": self.path, "contract_version": CONTRACT_VERSION}, 404)
            return
        try:
            self._respond(fn(payload))
        except Exception as exc:
            self._respond({"error": type(exc).__name__, "message": str(exc)}, 400)


class LoopbackServer:
    def __init__(self, dispatcher: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]], port: int = 8765):
        _Handler.dispatcher = dispatcher
        self.httpd = ThreadingHTTPServer((BIND_HOST, port), _Handler)
        self.httpd.daemon_threads = True
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()

    @property
    def address(self) -> str:
        host, port = self.httpd.server_address[:2]
        return f"http://{host}:{port}"

    @staticmethod
    def bind_description() -> Dict[str, str]:
        return {
            "bind_host": BIND_HOST,
            "note": "仅绑定本机回环地址；外部网卡地址访问不可达（4.3.6）",
        }