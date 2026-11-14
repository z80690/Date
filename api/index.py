"""Vercel serverless entrypoint (WSGI).

Minimal self-contained web handler used to get the deployment green.
The original drill adapter code (``adapter/`` package) is intentionally
left untouched; this entrypoint carries zero third-party dependencies.
"""

from __future__ import annotations

import json

SERVICE_NAME = "p003-drill-adapter"


class RequestHandler:
    """Minimal WSGI application: responds 200 OK with a JSON status body."""

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "/")
        payload = json.dumps(
            {"status": "ok", "service": SERVICE_NAME, "path": path}
        ).encode("utf-8")
        start_response(
            "200 OK",
            [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(payload))),
            ],
        )
        return [payload]


app = RequestHandler()
