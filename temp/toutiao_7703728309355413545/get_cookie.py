import re, sys, io, http.cookiejar
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.ixigua.com/",
})
# 第一步：访问主页拿基础 cookie（ttwid 等）
r0 = s.get("https://www.ixigua.com/", timeout=30)
print("home status:", r0.status_code)
print("cookies:", {c.name: c.value[:12] for c in s.cookies})

# 第二步：验证目标视频页
vid = "7703728309355413545"
r = s.get(f"https://www.ixigua.com/{vid}", timeout=30)
html = r.text
print("video page status:", r.status_code, "len:", len(html))
t = re.search(r"<title>([^<]*)</title>", html)
print("title:", t.group(1)[:80] if t else "NO_TITLE")
for pat in [r'"videoResource"[^\{]*\{', r'vid["\s:]+["\']?(\w{10,25})', r'"video_id"\s*:\s*"(\w+)"']:
    m = re.findall(pat, html)
    if m:
        print("PAT", pat[:25], "->", m[:3])

# 第三步：写 Netscape cookies.txt 给 yt-dlp
jar = http.cookiejar.MozillaCookieJar("cookies.txt")
for c in s.cookies:
    jar.set_cookie(c)
jar.save(ignore_discard=True, ignore_expires=True)
print("cookies.txt saved")