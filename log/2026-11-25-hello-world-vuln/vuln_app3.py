#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第三关靶机：带黑名单过滤的命令注入
- 只在 Kali 内部 127.0.0.1:8767 运行，不对外
- 故意留洞，用于本地教学，勿放到真实环境
- 防护只拦了 ; && | & 换行，漏了 $() 和反引号
"""
import json
import pathlib
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

FLAG = "/tmp/kali_flag.txt"
# 网站自称的"安全检查"：只挡这四个符号
BLACKLIST = [";", "&&", "|", "&", "%0a", "\n"]

# 启动时放一面旗，模拟"服务器上不该被读到的文件"
pathlib.Path(FLAG).write_text("FLAG{kali_cmd_injection_2026}\n", encoding="utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parts = urlparse(self.path)
        qs = parse_qs(parts.query)

        if parts.path == "/":
            body = (
                "<h1>Kali 系统健康检查</h1>"
                "<p>输入一个地址，系统帮你检查：</p>"
                '<form action="/check"><input name="target" value="127.0.0.1">'
                '<button type="submit">检查</button></form>'
                "<p>提示：本系统已开启安全检查，非法字符会被拦截。</p>"
            ).encode("utf-8")
            ctype = "text/html; charset=utf-8"

        elif parts.path == "/check":
            target = qs.get("target", [""])[0]
            low = target.lower()

            # 第一道门：黑名单。看着挺严，其实漏了两扇窗
            if any(b in low for b in BLACKLIST):
                result = {"error": "检测到非法字符，请求被拒绝"}
            else:
                # 第二道门：把输入直接拼进系统命令（洞就在这）
                cmd = "echo Checking host: " + target
                run = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=5
                )
                result = {"output": run.stdout.strip(), "target": target}
            body = json.dumps(result, ensure_ascii=False).encode("utf-8")
            ctype = "application/json; charset=utf-8"

        else:
            body = b'{"error":"not found"}'
            ctype = "application/json"

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # 不刷日志，干净


if __name__ == "__main__":
    print("靶机已启动: http://127.0.0.1:8767 (仅 Kali 内部)", flush=True)
    HTTPServer(("127.0.0.1", 8767), Handler).serve_forever()
