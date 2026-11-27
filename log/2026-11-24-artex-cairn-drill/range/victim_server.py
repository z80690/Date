"""靶机 Web 服务：绑定 127.0.0.4:8080，故意留一个目录穿越漏洞。
记录访问日志 artifacts/victim_access.log（CSV：ts,src_ip,xff,path,status）。
"""
import csv
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "artifacts", "victim_access.log")
WEBROOT = os.path.join(HERE, "webroot")


def log(src, xff, path, status):
    new = not os.path.exists(LOG)
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "src_ip", "x_forwarded_for", "path", "status"])
        import datetime
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), src, xff, path, status])


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        src = self.client_address[0]
        xff = self.headers.get("X-Forwarded-For", "-")
        if u.path == "/":
            body = b"ARTEX RANGE / victim app; try /file?name=..."
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            log(src, xff, self.path, 200)
            return
        if u.path == "/file":
            name = parse_qs(u.query).get("name", [""])[0]
            # 漏洞点：未校验 ../，可穿越到 webroot 之外
            target = os.path.normpath(os.path.join(WEBROOT, name))
            if os.path.isfile(target):
                with open(target, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                log(src, xff, self.path, 200)
            else:
                body = b"NOT FOUND"
                self.send_response(404)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                log(src, xff, self.path, 404)
            return
        self.send_response(404)
        self.end_headers()
        log(src, xff, self.path, 404)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    srv = HTTPServer(("127.0.0.4", port), H)
    print(f"victim listening 127.0.0.4:{port} pid={os.getpid()}", flush=True)
    srv.serve_forever()
