import base64, json, re, sys, io
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
data = json.loads(open("render_data.json", encoding="utf-8").read())
ai = data["articleInfo"]
token_b64 = ai["playAuthTokenV2"]
print("token b64 len:", len(token_b64))
tok = json.loads(base64.b64decode(token_b64 + "=" * (-len(token_b64) % 4)))
open("play_token.json", "w", encoding="utf-8").write(json.dumps(tok, ensure_ascii=False, indent=1))
print("token keys:", list(tok.keys()))
git = tok.get("GetPlayInfoToken", "")
print("GetPlayInfoToken head:", git[:200])

# 直接向字节跳动点播网关发起 GetPlayInfo
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
for host in ["https://vod.bytedance.com/api/vod/GetPlayInfo", "https://vod.snssdk.com/api/vod/GetPlayInfo"]:
    try:
        r = requests.get(host, params=git, headers={"User-Agent": UA, "Referer": "https://www.toutiao.com/"}, timeout=30)
        print("---", host, "status:", r.status_code, "len:", len(r.text))
        try:
            j = r.json()
            open("getplayinfo.json", "a", encoding="utf-8").write(json.dumps(j, ensure_ascii=False, indent=1) + "\n")
            txt = json.dumps(j, ensure_ascii=False)
            urls = re.findall(r'"(?:MainUrl|BackupUrl|Url|main_url|backup_url)"\s*:\s*"([^"]{15,220})"', txt)
            for u in urls[:6]:
                print("PLAY:", u[:200])
            if not urls:
                print(json.dumps(j, ensure_ascii=False)[:400])
        except Exception as ex:
            print("not json:", str(ex)[:80], r.text[:200])
    except Exception as e:
        print("ERR:", host, e)