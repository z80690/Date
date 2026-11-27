#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第四关靶机：上传功能 + 任意文件读取（掺沙子版）
- 只在 Kali 内部 127.0.0.1:8768 运行
- config/ 里的"密钥"全是编造的假数据，不是任何真实凭据
- 故意留洞：读取接口不检查 ..，演示"漏洞挖到之后会泄露什么"
- 不做提权、不做横移、不碰真实系统文件
"""
import json
import pathlib
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = pathlib.Path("/tmp/web4")
UPLOADS = ROOT / "uploads"
CONFIG = ROOT / "config"

# 启动时搭场景：上传目录 + 一份编造的假配置
UPLOADS.mkdir(parents=True, exist_ok=True)
CONFIG.mkdir(parents=True, exist_ok=True)
(CONFIG / "fake_secrets.env").write_text(
    "# ===== 本文件全是靶机编造的假数据，不是真实密钥 =====\n"
    "FAKE_DB_HOST=127.0.0.1\n"
    "FAKE_DB_USER=fake_admin\n"
    "FAKE_DB_PASS=THIS_IS_FAKE_DO_NOT_USE_12345\n"
    "FAKE_API_TOKEN=fake-token-0000000000\n",
    encoding="utf-8",
)


def parse_upload(body: bytes, boundary: bytes):
    """极简 multipart 解析，够教学用"""
    out = {}
    for part in body.split(b"--" + boundary):
        if b"Content-Disposition:" not in part:
            continue
        head, _, content = part.partition(b"\r\n\r\n")
        m = re.search(rb'filename="([^"]+)"', head)
        if m:
            out["filename"] = m.group(1).decode("utf-8", "ignore")
            out["content"] = content.rstrip(b"\r\n")
    return out


class Handler(BaseHTTPRequestHandler):
    def reply(self, body: bytes, ctype="text/plain; charset=utf-8", code=200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parts = urlparse(self.path)
        qs = parse_qs(parts.query)

        if parts.path == "/":
            page = (
                "<h1>文件上传演示站</h1>"
                '<form action="/upload" method="post" enctype="multipart/form-data">'
                '<input type="file" name="file"><button type="submit">上传</button></form>'
                '<p><a href="/view?name=note.txt">查看已上传文件</a></p>'
            )
            self.reply(page.encode("utf-8"), "text/html; charset=utf-8")

        elif parts.path == "/view":
            name = qs.get("name", [""])[0]
            # 洞就在这：直接拼路径，不拦 ..
            target = UPLOADS / name
            try:
                text = target.read_text(encoding="utf-8", errors="replace")
                self.reply(json.dumps({"file": name, "content": text}, ensure_ascii=False).encode("utf-8"),
                           "application/json; charset=utf-8")
            except Exception as e:
                self.reply(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"),
                           "application/json; charset=utf-8")

        else:
            self.reply(b'{"error":"not found"}', "application/json", 404)

    def do_POST(self):
        if self.path != "/upload":
            self.reply(b'{"error":"not found"}', "application/json", 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        ctype = self.headers.get("Content-Type", "")
        m = re.search(r"boundary=(.+)", ctype)
        if not m:
            self.reply(b'{"error":"no boundary"}', "application/json", 400)
            return
        info = parse_upload(body, m.group(1).strip().encode())
        name = info.get("filename", "noname")
        # 洞之一：文件名不做任何检查
        (UPLOADS / name).write_bytes(info.get("content", b""))
        self.reply(json.dumps({"ok": True, "saved": name}, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print("第四关靶机: http://127.0.0.1:8768 (仅 Kali 内部)", flush=True)
    HTTPServer(("127.0.0.1", 8768), Handler).serve_forever()
