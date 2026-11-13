import json, re, sys, io
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
UA_PC = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
s = requests.Session()
s.headers.update({"User-Agent": UA_PC, "Referer": "https://www.bilibili.com/"})

BVID = "BV1jd4g6fECp"
print("=== 1. video detail ===")
r = s.get("https://api.bilibili.com/x/web-interface/view", params={"bvid": BVID}, timeout=20)
j = r.json()
if j.get("code") == 0:
    d = j["data"]
    print("title:", d["title"])
    print("desc:", (d.get("desc") or "")[:400])
    print("mid:", d["owner"]["mid"], "| up:", d["owner"]["name"], "| fans_url_check")
    print("duration:", d["duration"], "pubdate:", d["pubdate"])
    mid = d["owner"]["mid"]
    json.dump(d, open("bili_workflows_video.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
else:
    print("ERR:", j.get("code"), j.get("message"))
    mid = None

if mid:
    print()
    print(f"=== 2. UP(all videos) mid={mid} ===")
    allv = []
    pn = 1
    while pn <= 4:
        r2 = s.get(
            "https://api.bilibili.com/x/space/wbi/arc/search",
            params={"mid": mid, "pn": pn, "ps": 30, "order": "pubdate"},
            timeout=20,
        )
        j2 = r2.json()
        if j2.get("code") != 0:
            print("list ERR:", j2.get("code"), str(j2.get("message"))[:80])
            break
        vlist = (j2.get("data", {}).get("list", {}) or {}).get("vlist") or []
        if not vlist:
            break
        allv.extend(vlist)
        pn += 1
    print("total found:", len(allv))
    for v in allv:
        print(f" - {v['title'][:56]} | bvid:{v['bvid']} | len:{v.get('length')} | play:{v.get('play')} | {v.get('created')}")
    json.dump(allv, open("bili_up_videos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)