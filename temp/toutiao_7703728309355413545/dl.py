import json, re, sys, io
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
j = json.load(open("getplayinfo.json", encoding="utf-8"))
pil = j["Result"]["Data"]["PlayInfoList"]
best = None
for item in pil:
    defn = item.get("Definition", "")
    main = item.get("MainPlayUrl", "")
    size = item.get("FileSize", 0)
    print(f"Definition={defn} size={size} main={main[:120]}")
    if main and (best is None or "720p" in str(defn) or (best and size > best[0])):
        if "720p" in str(defn) or best is None:
            best = (size, main, defn)

# 按记忆口径优先 720p；都没有就取第一个有 MainPlayUrl 的
main_url = None
for item in pil:
    d = str(item.get("Definition", ""))
    if "720p" in d and item.get("MainPlayUrl"):
        main_url = item["MainPlayUrl"]
        print("picked 720p, def=", d)
        break
if not main_url:
    for item in pil:
        if item.get("MainPlayUrl"):
            main_url = item["MainPlayUrl"]
            print("picked fallback, def=", item.get("Definition"))
            break

assert main_url, "no MainPlayUrl found"
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
r = requests.get(main_url, headers={"User-Agent": UA, "Referer": "https://m.toutiao.com/"}, timeout=120, stream=True)
print("video download status:", r.status_code, "len:", r.headers.get("Content-Length"))
n = 0
with open("video.mp4", "wb") as f:
    for chunk in r.iter_content(1 << 20):
        f.write(chunk)
        n += len(chunk)
print("saved bytes:", n)