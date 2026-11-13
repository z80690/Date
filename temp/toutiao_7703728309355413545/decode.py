import re, sys, io, json
from urllib.parse import unquote

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
html = open("mobile_page.html", encoding="utf-8").read()

print("=== block 0: VideoObject JSON-LD ===")
m = re.search(r'<script[^>]*>\s*(\{"@context".*?)\s*</script>', html, re.S)
if m:
    obj = json.loads(m.group(1))
    open("videoobject.json", "w", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False, indent=1))
    print(json.dumps(obj, ensure_ascii=False, indent=1)[:1500])

print()
print("=== block 5: RENDER_DATA ===")
m5 = re.search(r'<script[^>]*id="RENDER_DATA"[^>]*>(.*?)</script>', html, re.S)
if m5:
    data = unquote(m5.group(1))
    open("render_data.json", "w", encoding="utf-8").write(data)
    print("decoded len:", len(data))
    obj5 = json.loads(data)
    def walk(o, path="", depth=0):
        if depth > 4:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and ("http" in v and (".mp4" in v or "douyinvod" in v or "video" in v.lower() and "url" in path.lower())):
                    print(f"{path}.{k} => {v[:160]}")
                elif k in ("videoUrl", "video_url", "playUrl", "main_url", "backup_url", "video_4k_url", "download_url"):
                    print(f"{path}.{k} => {str(v)[:160]}")
                else:
                    walk(v, f"{path}.{k}", depth + 1)
        elif isinstance(o, list):
            for i, v in enumerate(o[:3]):
                walk(v, f"{path}[{i}]", depth + 1)
    walk(obj5)
    print("--- top keys:", list(obj5.keys())[:10])