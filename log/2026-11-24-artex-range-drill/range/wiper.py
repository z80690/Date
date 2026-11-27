"""痕迹擦除模块（演练用）：从各跳板/靶机日志中删除含攻击特征的记录行。
保留被删前的行到 artifacts/wiped_rows.json 作为取证对照。
用法: wiper.py <keyword>
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "artifacts")
KEYWORD = sys.argv[1] if len(sys.argv) > 1 else "../secrets"
LOGS = ["victim_access.log", "jump_j1_access.log", "jump_j2_access.log"]
report = {"keyword": KEYWORD, "files": {}}

for name in LOGS:
    p = os.path.join(ART, name)
    if not os.path.exists(p):
        report["files"][name] = {"status": "missing"}
        continue
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
        "status": "wiped",
        "before_lines": len(body),
        "after_lines": len(kept),
        "removed_lines": len(removed),
        "removed_rows": [r.strip() for r in removed],
    }

out = os.path.join(ART, "wiped_rows.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(json.dumps(report, ensure_ascii=False, indent=2))
