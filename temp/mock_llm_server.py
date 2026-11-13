"""P003 G2.4 local placeholder LLM endpoint (OpenAI-compatible, loopback only).

Serves deterministic non-empty responses so framework LLM configs are valid and
any accidental model call lands on 127.0.0.1 instead of a cloud endpoint.
Real decisions come from the CodeArts agent (plan-a receipt mode). No network
egress: binds 127.0.0.1 only, never calls out.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST, PORT = "127.0.0.1", 7810


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/v1/models"):
            self._reply(200, {"object": "list", "data": [{"id": "placeholder", "object": "model"}]})
        elif self.path.startswith("/health"):
            self._reply(200, {"status": "ok", "mode": "placeholder"})
        else:
            self._reply(404, {"error": {"message": "placeholder endpoint"}})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length:
            self.rfile.read(length)
        content = "[placeholder] deterministic response; decisions are made by the CodeArts agent (plan-a receipt mode)."
        self._reply(200, {
            "id": "chatcmpl-placeholder",
            "object": "chat.completion",
            "created": 0,
            "model": "placeholder",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        })

    def log_message(self, fmt, *args):
        print("[mock-llm] %s" % (fmt % args), flush=True)


if __name__ == "__main__":
    print("[mock-llm] listening on http://%s:%d (loopback only)" % (HOST, PORT), flush=True)
    HTTPServer((HOST, PORT), Handler).serve_forever()