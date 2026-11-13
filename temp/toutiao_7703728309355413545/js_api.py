import requests, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
js = requests.get(
    "https://lf-dw.toutiaostatic.com/obj/toutiao-duanwai/mobile_share/ssr/cn/pages/short_video/index.ff08d01b.js",
    timeout=30,
).text
print("js len:", len(js))
open("share_page.js", "w", encoding="utf-8").write(js)
apis = set()
for m in re.findall(r'"(/[\w/\-.]{4,50}(?:api|info|video|detail|stream|play)[\w/\-.]{0,40})"', js):
    apis.add(m)
for m in sorted(apis)[:40]:
    print("API:", m)
for m in sorted(set(re.findall(r'(https?://[\w\-.]{6,50}\.(?:toutiao|snssdk|iesdouyin|zjcdn)[\w\-.]{0,30}/[\w/\-.]{0,40})', js)))[:15]:
    print("HOST:", m)