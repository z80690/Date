"""跳板机：绑定本机回环某 IP:端口，把流量转发到下一跳，记录每一跳日志。
CSV：ts,src_ip,dst,path,chain(来源经过的跳板链)。
用法: jump_host.py <listen_ip> <listen_port> <next_ip:port> <jump_label>
"""
import csv
import datetime
import os
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
NEXT = sys.argv[3]
LABEL = sys.argv[4]
LOG = os.path.join(HERE, "artifacts", f"jump_{LABEL}_access.log")


def log(src, chain, path):
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "src_ip", "dst", "path", "chain"])
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), src, NEXT, path, chain])


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        src = self.client_address[0]
        old = self.headers.get("X-Forwarded-For", "")
        chain = f"{old} -> {src}" if old else src
        url = f"http://{NEXT}{self.path}"
        req = urllib.request.Request(url)
        req.add_header("X-Forwarded-For", chain)
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                body = r.read()
                code = r.status
        except urllib.error.HTTPError as e:
            body = e.read()
            code = e.code
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        log(src, chain, self.path)


if __name__ == "__main__":
    listen_ip = sys.argv[1]
    port = int(sys.argv[2])
    srv = HTTPServer((listen_ip, port), H)
    print(f"jump {LABEL} listening {listen_ip}:{port} -> {NEXT} pid={os.getpid()}", flush=True)
    srv.serve_forever()
