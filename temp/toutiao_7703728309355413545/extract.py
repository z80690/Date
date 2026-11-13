import re, sys, io, json, html as ihtml
from urllib.parse import unquote

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
html = open("mobile_page.html", encoding="utf-8").read()

print("=== video tags ===")
for m in re.findall(r"<video[^>]*>", html)[:5]:
    print(m[:200])

print("=== src/href with mp4 or v ===")
for m in re.findall(r'(?:src|href)="([^"]*(?:mp4|douyinvod|zjcdn|douyin|video)[^"]*)"', html)[:10]:
    print(unquote(m)[:180])

print("=== json blobs keys ===")
for m in re.findall(r'"(videoUrl|video_url|playUrl|play_url|main_url|backup_url|video_list|videoResource|vid|item_id|group_id)"', html)[:20]:
    print("key:", m)

print("=== any http video url ===")
for m in re.findall(r'https?://[^"\'\\\s]{20,180}(?:\.mp4|douyinvod[^"\'\\\s]{0,80}|zjcdn[^"\'\\\s]{0,80})', html)[:6]:
    print(unquote(m)[:200])

print("=== description / text content ===")
t = re.search(r'<meta name="description" content="([^"]*)"', html)
print("meta desc:", ihtml.unescape(t.group(1))[:300] if t else "NONE")
texts = re.findall(r"<p[^>]*>([^<]{10,200})</p>", html)
for x in texts[:12]:
    print("P:", ihtml.unescape(x).strip()[:150])

print("=== author ===")
for pat in [r'"nick_?name"\s*:\s*"([^"]{2,40})"', r'"user_?name"\s*:\s*"([^"]{2,40})"', r'class="[^"]*author[^"]*"[^>]*>([^<]{2,40})<']:
    m = re.findall(pat, html)
    if m:
        print("PAT", pat[:28], "->", m[:3])