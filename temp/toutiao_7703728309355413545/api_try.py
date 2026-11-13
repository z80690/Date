import json, re, sys, io
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
MOBILE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
s = requests.Session()
s.headers.update({"User-Agent": MOBILE_UA, "Referer": "https://m.toutiao.com/video/7703728309355413545/"})
vid = "7703728309355413545"

print("=== try slow_info ===")
try:
    r = s.get(
        f"https://m.toutiao.com/i{vid}/slow_info/",
        params={"app_name": "mobile_detail_web", "app_id": 1286, "os": "web", "device_platform": "web"},
        timeout=30,
    )
    print("status:", r.status_code, "len:", len(r.text))
    try:
        data = r.json()
        print("success:", data.get("success"))
        open("slow_info.json", "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=1))
        txt = json.dumps(data, ensure_ascii=False)
        for key in ["video_4k_url", "video_url", "main_url", "backup_url", "download_url", "play_addr"]:
            m = re.search(rf'"{key}"\s*:\s*"([^"]{{10,200}})"', txt)
            if m:
                print("FOUND", key, ":", m.group(1)[:150])
        m = re.search(r'"title"\s*:\s*"([^"]{5,100})"', txt)
        if m:
            print("TITLE:", m.group(1))
    except Exception as ex:
        print("not json:", str(ex)[:100], r.text[:200])
except Exception as e:
    print("ERR:", e)

print("=== try lvideo api ===")
try:
    r2 = s.get(
        "https://m.toutiao.com/vapp/lvideo/api/info/",
        params={"aid": 13, "app_name": "news_article", "share_from": "news_article", "episode_id": vid, "image_format": "jpeg"},
        timeout=30,
    )
    print("status:", r2.status_code, "len:", len(r2.text))
    try:
        data2 = r2.json()
        open("lvideo.json", "w", encoding="utf-8").write(json.dumps(data2, ensure_ascii=False, indent=1))
        txt2 = json.dumps(data2, ensure_ascii=False)
        for key in ["video_4k_url", "video_url", "main_url", "backup_url", "download_url"]:
            m = re.search(rf'"{key}"\s*:\s*"([^"]{{10,200}})"', txt2)
            if m:
                print("FOUND", key, ":", m.group(1)[:150])
        m = re.search(r'"title"\s*:\s*"([^"]{5,100})"', txt2)
        if m:
            print("TITLE:", m.group(1))
    except Exception as ex:
        print("not json:", str(ex)[:100], r2.text[:200])
except Exception as e:
    print("ERR:", e)