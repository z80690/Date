import json, re, sys, io, time
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
UA_PC = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
s = requests.Session()
s.headers.update({"User-Agent": UA_PC, "Referer": "https://www.bilibili.com/"})

print("=== A. search enumerate 欧工Ai videos ===")
allv = {}
for pn in range(1, 4):
    r = s.get(
        "https://api.bilibili.com/x/web-interface/wbi/search/type",
        params={"search_type": "video", "keyword": "欧工Ai", "page": pn},
        timeout=20,
    )
    j = r.json()
    if j.get("code") != 0:
        print("search ERR:", j.get("code"), str(j.get("message"))[:80])
        break
    res = j.get("data", {}).get("result") or []
    if not res:
        break
    for v in res:
        if v.get("author") == "欧工Ai":
            allv[v["bvid"]] = {
                "title": re.sub(r"<[^>]+>", "", v.get("title", "")),
                "bvid": v.get("bvid"),
                "play": v.get("play"),
                "pubdate": v.get("pubdate"),
                "description": (v.get("description") or "")[:200],
            }
    time.sleep(1)
print("ougongai videos:", len(allv))
for v in allv.values():
    print(f" - {v['title'][:60]} | {v['bvid']} | play:{v['play']} | pub:{v['pubdate']}")
    print(f"   desc: {v['description'][:150]}")
json.dump(list(allv.values()), open("bili_ougongai_all.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print()
print("=== B. player subtitle check for BV1jd4g6fECp ===")
try:
    detail = json.load(open("bili_workflows_video.json", encoding="utf-8"))
    cid = detail["pages"][0]["cid"]
    r2 = s.get("https://api.bilibili.com/x/player/v2", params={"bvid": "BV1jd4g6fECp", "cid": cid}, timeout=20)
    j2 = r2.json()
    print("player v2 code:", j2.get("code"))
    sub = (j2.get("data", {}) or {}).get("subtitle", {}) or {}
    subs = sub.get("subtitles") or []
    print("subtitles:", len(subs))
    for x in subs:
        print(" -", x.get("lan_doc"), x.get("subtitle_url", "")[:100])
        if x.get("subtitle_url"):
            su = x["subtitle_url"].replace("http://", "https://")
            cs = s.get(su, timeout=20).json()
            lines = [seg.get("content", "") for seg in cs.get("body", [])]
            open("bili_sub_workflows.txt", "w", encoding="utf-8").write("\n".join(lines))
            print("   saved subtitle lines:", len(lines))
except Exception as e:
    print("ERR:", str(e)[:150])