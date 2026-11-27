"""故意留越权漏洞的最小靶机（Hello World 级别）。仅绑 127.0.0.1。"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# 模拟数据库：两个用户的订单
DB = {
    "1": {"user": "alice", "orders": ["订单A-001 手机 5999元"]},
    "2": {"user": "bob", "orders": ["订单B-001 电脑 8999元", "订单B-002 硬盘 599元"]},
}

# 故意留洞：只看参数 user_id，不校验登录态 -> 越权
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        if urlparse(self.path).path == "/api/orders":
            uid = q.get("user_id", [""])[0]
            if uid in DB:
                body = json.dumps({"user": DB[uid]["user"], "orders": DB[uid]["orders"]}, ensure_ascii=False)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
            else:
                body = json.dumps({"error": "not found"}, ensure_ascii=False)
                self.send_response(404)
                self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("X-Target-Note", "HELLO-WORLD-VULN-DEMO")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>Hello World Vuln Demo</h1><p>Try /api/orders?user_id=1</p>")

if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
