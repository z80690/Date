import io, sys, json, re, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
UA = {"User-Agent": "Mozilla/5.0"}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


def get_text(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


print("=== 1. matinrco/tor releases ===")
try:
    rels = get_json("https://api.github.com/repos/matinrco/tor/releases?per_page=3")
    for r in rels[:2]:
        print("TAG:", r["tag_name"])
        for a in r.get("assets", []):
            print("  ASSET:", a["name"], round(a["size"] / 1048576, 1), "MB ->", a["browser_download_url"][:95])
except Exception as e:
    print("ERR:", type(e).__name__, str(e)[:90])

print("=== 2. onionshare/onionshare releases (win assets) ===")
try:
    rels = get_json("https://api.github.com/repos/onionshare/onionshare/releases?per_page=2")
    for r in rels[:2]:
        print("TAG:", r["tag_name"])
        for a in r.get("assets", []):
            n = a["name"].lower()
            if "win" in n or "exe" in n:
                print("  ASSET:", a["name"], round(a["size"] / 1048576, 1), "MB")
except Exception as e:
    print("ERR:", type(e).__name__, str(e)[:90])

print("=== 3. rigwild/tor-downloader source URLs ===")
for branch in ("main", "master"):
    try:
        txt = get_text(f"https://raw.githubusercontent.com/rigwild/tor-downloader/{branch}/README.md")
        urls = re.findall(r"https?://[^\s\)\]\"']+", txt)
        for u in urls[:8]:
            print("  URL:", u[:110])
        break
    except Exception as e:
        print("  branch", branch, "ERR:", type(e).__name__, str(e)[:60])