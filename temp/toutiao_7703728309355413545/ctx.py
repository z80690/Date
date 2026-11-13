import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
js = open("share_page.js", encoding="utf-8").read()
for kw in ["lvideo/api/info", "slow_info"]:
    for m in re.finditer(re.escape(kw), js):
        s, e = max(0, m.start() - 300), min(len(js), m.end() + 400)
        seg = js[s:e]
        seg = seg.replace("\n", " ")
        print("=== CTX", kw, "===")
        print(seg[:650])
        print()