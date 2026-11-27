"""进阶关卡：故意留 SQL 注入洞的登录接口。仅绑 127.0.0.1，内存数据库，不碰真实文件。"""
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (username TEXT, password TEXT)")
conn.executemany("INSERT INTO users VALUES (?,?)", [("admin", "S3cret!"), ("alice", "p4ss")])
conn.commit()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path == "/login":
            name = q.get("u", [""])[0]
            pwd = q.get("p", [""])[0]
            sql = f"SELECT username FROM users WHERE username='{name}' AND password='{pwd}'"
            rows = conn.execute(sql).fetchall()
            ok = len(rows) > 0
            body = json.dumps({"login": "SUCCESS" if ok else "FAIL", "matched": [r[0] for r in rows]}, ensure_ascii=False)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>Level 2 - SQLi demo</h1><p>Try /login?u=admin&p=wrong</p>")

if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8766), Handler).serve_forever()
