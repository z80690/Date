"""痕迹擦除：从所有跳板链日志 + 靶机日志中删含攻击特征的记录行。
动态发现 chain_*.log / victim_access.log，不写死跳板数。
用法: wiper.py <keyword>
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "artifacts")
KEYWORD = sys.argv[1] if len(sys.argv) > 1 else "../secrets"
logs = sorted(glob.glob(os.path.join(ART, "chain_*.log")))
vp = os.path.join(ART, "victim_access.log")
if os.path.exists(vp):
    logs.append(vp)
report = {"keyword": KEYWORD, "file_count": len(logs), "files": {}}

for p in logs:
    name = os.path.basename(p)
    with open(p, encoding="utf-8") as f:
        lines = f.readlines()
    header = lines[0] if lines else ""
    body = lines[1:] if lines else []
    kept = [ln for ln in body if KEYWORD not in ln]
    removed = [ln for ln in body if KEYWORD in ln]
    with open(p, "w", encoding="utf-8") as f:
        f.write(header)
        f.writelines(kept)
    report["files"][name] = {
        "before": len(body), "after": len(kept), "removed": len(removed),
        "removed_rows": [r.strip() for r in removed],
    }

out = os.path.join(ART, "wiped_rows.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(json.dumps({"file_count": len(logs),
                  "total_removed": sum(v["removed"] for v in report["files"].values())},
                 ensure_ascii=False))
