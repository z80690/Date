import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
data = open("render_data.json", encoding="utf-8").read()
# 全文直接找 URL 模式
for pat in [r'https?://[^"\\ ]{15,250}\.mp4[^"\\ ]{0,60}', r'https?://[^"\\ ]*douyinvod[^"\\ ]{0,150}', r'https?://[^"\\ ]*video[^"\\ ]{0,150}']:
    ms = re.findall(pat, data)
    for m in ms[:5]:
        print("URL:", m[:220])
print("---articleInfo keys---")
obj = json.loads(data)
ai = obj.get("articleInfo", {})
print(json.dumps({k: (str(v)[:100] if not isinstance(v, (dict, list)) else type(v).__name__) for k, v in ai.items()}, ensure_ascii=False, indent=1)[:1200])
open("article_info.json", "w", encoding="utf-8").write(json.dumps(ai, ensure_ascii=False, indent=1))