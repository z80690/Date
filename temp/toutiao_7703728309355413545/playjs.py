import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
js = open("share_page.js", encoding="utf-8").read()
for kw in ["GetPlayInfo", "playInfo", "douyinvod", "stream_url", "get_stream", "videoPlayUrl", "play_url", "PlayUrl"]:
    idxs = [m.start() for m in re.finditer(re.escape(kw), js)]
    print(f"=== {kw}: {len(idxs)} hits")
    for ix in idxs[:2]:
        seg = js[max(0, ix - 250):ix + 350].replace("\n", " ")
        print("   ...", seg[:550])
        print()