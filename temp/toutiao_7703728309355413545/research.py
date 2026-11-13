import json, re, sys, io
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
UA_PC = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

print("=== 1. bilibili search: 欧工Ai ===")
try:
    r = requests.get(
        "https://api.bilibili.com/x/web-interface/wbi/search/type",
        params={"search_type": "video", "keyword": "欧工Ai 单片机", "page": 1},
        headers={"User-Agent": UA_PC, "Referer": "https://www.bilibili.com/"},
        timeout=20,
    )
    print("status:", r.status_code, "code:", r.json().get("code"))
    res = r.json().get("data", {}).get("result") or []
    for v in res[:8]:
        t = re.sub(r"<[^>]+>", "", v.get("title", ""))
        print(f" - {t[:60]} | up:{v.get('author')} | play:{v.get('play')} | bvid:{v.get('bvid')} | {v.get('pubdate')}")
except Exception as e:
    print("ERR:", str(e)[:150])

print()
print("=== 2. bilibili search: AI 单片机 工作流 ===")
try:
    r = requests.get(
        "https://api.bilibili.com/x/web-interface/wbi/search/type",
        params={"search_type": "video", "keyword": "AI 单片机 项目 工作流", "page": 1},
        headers={"User-Agent": UA_PC, "Referer": "https://www.bilibili.com/"},
        timeout=20,
    )
    res = r.json().get("data", {}).get("result") or []
    for v in res[:8]:
        t = re.sub(r"<[^>]+>", "", v.get("title", ""))
        print(f" - {t[:60]} | up:{v.get('author')} | bvid:{v.get('bvid')}")
except Exception as e:
    print("ERR:", str(e)[:150])

print()
print("=== 3. toutiao author profile (mobile) ===")
try:
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"})
    r = s.get("https://m.toutiao.com/profile/3736609008662828/", timeout=20)
    print("profile status:", r.status_code, "len:", len(r.text))
    t = re.search(r"<title>([^<]*)</title>", r.text)
    print("title:", t.group(1)[:80] if t else "NO_TITLE")
    open("author_page.html", "w", encoding="utf-8").write(r.text)
    m5 = re.search(r'<script[^>]*id="RENDER_DATA"[^>]*>(.*?)</script>', r.text, re.S)
    if m5:
        from urllib.parse import unquote
        data = unquote(m5.group(1))
        open("author_render.json", "w", encoding="utf-8").write(data)
        print("RENDER_DATA decoded len:", len(data))
except Exception as e:
    print("ERR:", str(e)[:150])

print()
print("=== 4. douyin search ougongai ===")
try:
    r = requests.get(
        "https://www.douyin.com/aweme/v1/web/search/item/",
        params={"keyword": "欧工Ai", "count": 10},
        headers={"User-Agent": UA_PC, "Referer": "https://www.douyin.com/"},
        timeout=20,
    )
    print("douyin status:", r.status_code, r.text[:120])
except Exception as e:
    print("ERR:", str(e)[:150])