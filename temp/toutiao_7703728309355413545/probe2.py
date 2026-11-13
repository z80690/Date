import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
html = open("page.html", encoding="utf-8").read()
print("SCRIPT_DATA:", "SCRIPT_DATA" in html, "| RENDER_DATA:", "RENDER_DATA" in html, "| window.__:", "window.__" in html)
for m in re.findall(r'<script[^>]*id="([^"]+)"', html):
    print("script_id:", m)
print("---script srcs---")
for m in re.findall(r'src="([^"]+\.js[^"]*)"', html)[:8]:
    print(m)
t = re.search(r"<title>([^<]*)</title>", html)
print("---title:", t.group(1) if t else "NO_TITLE")
print("---iframe:", re.findall(r'<iframe[^>]*src="([^"]+)"', html)[:3])
print("---video tag:", re.findall(r'<video[^>]*>', html)[:2])
print("---any vid-like:", re.findall(r'["\']?vid["\']?[:=]\s*["\']?([\w\-]{6,30})', html)[:5])