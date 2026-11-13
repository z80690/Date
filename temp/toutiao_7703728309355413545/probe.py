import re, sys, io, json
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
url = "https://www.toutiao.com/video/7703728309355413545/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.toutiao.com/",
}
r = requests.get(url, headers=headers, timeout=30)
html = r.text
with open("page.html", "w", encoding="utf-8") as f:
    f.write(html)
print("status:", r.status_code, "len:", len(html))
for pat in [r'"vid"\s*:\s*"([^"]+)"', r'vid=(\d+)', r'video_id["\s:]+(\w+)', r'"video_4k_url"\s*:\s*"([^"]{10,120})', r'"video_url"\s*:\s*"([^"]{10,120})', r'"play_url"\s*:\s*"([^"]{10,120})', r'ixigua\.com/(\d+)', r'"title"\s*:\s*"([^"]{5,80})"']:
    ms = re.findall(pat, html)
    if ms:
        print("PAT", pat[:30], "->", ms[:3])
if "登录" in html or "login" in html.lower():
    print("HAS_LOGIN_HINT")