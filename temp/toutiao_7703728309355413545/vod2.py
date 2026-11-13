import base64, json, re, sys, io
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
tok = json.loads(open("play_token.json", encoding="utf-8").read())
git = tok["GetPlayInfoToken"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

url = "https://vod.snssdk.com/api/vod/GetPlayInfo?" + git
r = requests.get(url, headers={"User-Agent": UA, "Referer": "https://www.toutiao.com/"}, timeout=30)
print("status:", r.status_code, "len:", len(r.text))
j = r.json()
open("getplayinfo.json", "w", encoding="utf-8").write(json.dumps(j, ensure_ascii=False, indent=1))
txt = json.dumps(j, ensure_ascii=False)
urls = re.findall(r'"(?:MainUrl|BackupUrl|Url|main_url|backup_url)"\s*:\s*"([^"]{15,300})"', txt)
seen = set()
for u in urls:
    if u not in seen:
        seen.add(u)
        print("PLAY:", u[:230])
if not urls:
    err = j.get("ResponseMetadata", {}).get("Error")
    print("ERR:", err)
    print(txt[:500])