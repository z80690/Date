import json, re, sys, io
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
tok = json.loads(open("play_token.json", encoding="utf-8").read())
git = tok["GetPlayInfoToken"]
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

url = "https://vod.bytedanceapi.com/?" + git
r = requests.get(url, headers={"User-Agent": UA, "Referer": "https://m.toutiao.com/"}, timeout=30)
print("status:", r.status_code, "len:", len(r.text))
j = r.json()
open("getplayinfo.json", "w", encoding="utf-8").write(json.dumps(j, ensure_ascii=False, indent=1))
try:
    pil = j["Result"]["Data"]["PlayInfoList"]
    for k, v in pil.items():
        main = v.get("MainPlayUrl", "")
        backup = v.get("BackupPlayUrl", "")
        print(f"[{k}] main: {main[:180]}")
        if backup:
            print(f"[{k}] backup: {backup[:120]}")
    print("OK_DONE")
except Exception as e:
    print("structure miss:", str(e)[:100])
    print(json.dumps(j, ensure_ascii=False)[:600])