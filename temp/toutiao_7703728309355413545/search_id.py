import re, sys, io
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
})

def search(q):
    r = s.get("https://www.bing.com/search", params={"q": q, "setmkt": "zh-CN"}, timeout=30)
    html = r.text
    out = []
    for m in re.findall(r'<h2><a[^>]*href="([^"]+)"[^>]*>(.*?)</a></h2>', html)[:8]:
        title = re.sub(r"<[^>]+>", "", m[1])
        out.append((title[:70], m[0][:100]))
    return out

for q in ["toutiao 7703728309355413545", "头条视频 7703728309355413545", "欧工 嵌入式 开发 工作流 视频", "欧工 单片机 开发流程"]:
    print("=== Q:", q)
    try:
        for t, u in search(q):
            print(" -", t, "|", u)
    except Exception as e:
        print("ERR:", e)