import re, sys, io, json
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
MOBILE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

print("=== 1. toutiao mobile with mobile UA ===")
try:
    r = requests.get(
        "https://m.toutiao.com/video/7703728309355413545/",
        headers={"User-Agent": MOBILE_UA, "Referer": "https://m.toutiao.com/"},
        timeout=30,
    )
    html = r.text
    print("status:", r.status_code, "len:", len(html))
    t = re.search(r"<title>([^<]*)</title>", html)
    print("title:", t.group(1)[:100] if t else "NO_TITLE")
    print("has jsvmprt:", "jsvmprt" in html)
    for pat in [r'"video_4k_url"\s*:\s*"([^"]{10,150})"', r'"video_url"\s*:\s*"([^"]{10,150})"', r'"main_url"\s*:\s*"([^"]{10,150})"', r'"url_list"\s*:\s*\["([^"]{10,150})"', r'"vid"\s*:\s*"(\w{10,30})"', r'"title"\s*:\s*"([^"]{5,80})"']:
        m = re.findall(pat, html)
        if m:
            print("PAT", pat[:30], "->", m[:2])
    open("mobile_page.html", "w", encoding="utf-8").write(html)
except Exception as e:
    print("ERR:", e)

print("=== 2. sogou search video id ===")
try:
    r = requests.get(
        "https://www.sogou.com/web",
        params={"query": "7703728309355413545"},
        headers={"User-Agent": MOBILE_UA},
        timeout=30,
    )
    print("status:", r.status_code, "len:", len(r.text))
    for m in re.findall(r'<h3[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.S)[:6]:
        title = re.sub(r"<[^>]+>", "", m[1]).strip()
        if title:
            print(" -", title[:70], "|", m[0][:90])
except Exception as e:
    print("ERR:", e)

print("=== 3. sogou search ougong embed ===")
try:
    r = requests.get(
        "https://www.sogou.com/web",
        params={"query": "欧工 嵌入式 视频 开发"},
        headers={"User-Agent": MOBILE_UA},
        timeout=30,
    )
    print("status:", r.status_code, "len:", len(r.text))
    for m in re.findall(r'<h3[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.S)[:8]:
        title = re.sub(r"<[^>]+>", "", m[1]).strip()
        if title:
            print(" -", title[:70], "|", m[0][:90])
except Exception as e:
    print("ERR:", e)