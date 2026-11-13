import re, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
html = open("mobile_page.html", encoding="utf-8").read()
scripts = re.findall(r"<script([^>]*)>(.*?)</script>", html, re.S)
print("script blocks:", len(scripts))
for i, (attrs, body) in enumerate(scripts):
    body_s = body.strip()
    if not body_s:
        continue
    tag = re.search(r'id="([^"]+)"', attrs)
    print(f"--- block {i}: len={len(body_s)} id={tag.group(1) if tag else None} head={body_s[:120]!r}")
    if "video" in body_s.lower() or "play" in body_s.lower() or "initial" in body_s.lower():
        print("   >>> has video/play/initial keyword")
        open(f"block_{i}.txt", "w", encoding="utf-8").write(body_s)