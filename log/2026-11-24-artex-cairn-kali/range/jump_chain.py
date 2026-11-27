"""通用跳板节点：监听 127.0.0.<idx+1>:<port>，转发到下一跳，逐层追加 XFF。
用法: jump_chain.py <listen_ip> <listen_port> <next_ip:port> <index> <total>
日志: artifacts/chain_<index>_of_<total>.log  CSV: ts,src_ip,next,xff_chain,path
"""
import csv
import datetime
import os
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
LISTEN_IP = sys.argv[1]
PORT = int(sys.argv[2])
NEXT = sys.argv[3]
INDEX = sys.argv[4]
TOTAL = sys.argv[5]
LOG = os.path.join(HERE, "artifacts", f"chain_{INDEX}_of_{TOTAL}.log")


def log(src, nxt, chain, path):
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "src_ip", "next", "xff_chain", "path"])
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), src, nxt, chain, path])


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        src = self.client_address[0]
        old = self.headers.get("X-Forwarded-For", "")
        hop = f"H{INDEX}({LISTEN_IP}:{PORT})"
        chain = f"{old} -> {hop}" if old else hop
        url = f"http://{NEXT}{self.path}"
        req = urllib.request.Request(url)
        req.add_header("X-Forwarded-For", chain)
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                body, code = r.read(), r.status
        except urllib.error.HTTPError as e:
            body, code = e.read(), e.code
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        log(src, NEXT, chain, self.path)


if __name__ == "__main__":
    srv = HTTPServer((LISTEN_IP, PORT), H)
    print(f"hop {INDEX}/{TOTAL} listening {LISTEN_IP}:{PORT} -> {NEXT} pid={os.getpid()}", flush=True)
    srv.serve_forever()
