"""底座机制闭环验证驱动（任务 3.4/3.5/4.1/4.3 可运行验证）。

输出全部直写 UTF-8 文件落 04_测试验证（控制台不做中文输出）。
说明：本脚本验证底座受理链/回执/状态机机制闭环（tasks 2.x/3.x 判据），
非任务 6.1 的模拟器宿主（该任务锁定在 G2 门禁之后）。
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "04_测试验证")
os.makedirs(OUT_DIR, exist_ok=True)

from workflow_base.cli import Base, DATA_DIR
from workflow_base.adapters import embedded
from workflow_base.core.server import LoopbackServer

report = {"sections": []}

def out_json(name, payload):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    return path

# 1) 默认挂载 + 类目树（3.4 家电占位 + 5.3.1 规则 10 扩展标注）
base = Base()
mount_result = base.mount_defaults()
tree = base.catalogs.tree()
report["sections"].append({"section": "mount_and_tree", "mounted": mount_result["mounted"], "tree": tree})

# 2) 预留类目启动拒绝（5.1.1 规则 3）
try:
    base.scheduler.start_task("appliance_repair", "x", "y", {})
    reserved_check = {"pass": False, "note": "未拒绝"}
except Exception as exc:
    reserved_check = {"pass": "仅预留接口" in str(exc), "error_code": getattr(exc, "code", ""), "message": str(exc)}
report["sections"].append({"section": "reserved_start_rejected", "result": reserved_check})

# 3) 小智机制闭环：注册 → 上线 → 心跳 → 下发 → 回执 → 状态闭环（3.5/2.3/2.4/2.5）
obj = base.register_xiaozhi_sim()
base.environment.declare_environment(embedded.CATALOG_ID, embedded.CATALOG_CONTRACT["env_declaration"])
route = base.environment.route(embedded.CATALOG_ID, windows_available=True)
task = base.scheduler.start_task(embedded.CATALOG_ID, obj["object_id"], "send_text", {"text": "你好，底座"})
tid = task["task_id"]

# 模拟设备侧执行（机制验证桩，非 6.1 模拟器宿主）
normalized = embedded.normalize({"ok": True, "reply": f"echo: {task['params']['text']}"})
receipt_result = base.receipts.submit(tid, normalized["conclusion"], normalized["detail"])
final = base.scheduler.query(tid)

report["sections"].append({
    "section": "xiaozhi_loop",
    "object": obj,
    "route": route,
    "task_id": tid,
    "dispatch": task.get("dispatch"),
    "receipt": receipt_result["receipt"],
    "final_status": final["status"],
    "events": final["events"],
})

# 4) 自检（四项必列 + 三项附加，4.3）
selfcheck = base.environment.selfcheck()
report["sections"].append({"section": "selfcheck", "report": selfcheck})

# 5) 回环绑定说明（2.13）
report["sections"].append({"section": "loopback_bind", "bind": LoopbackServer.bind_description()})

# 6) 核心无领域字样检查（5.1.1 规则 4，判据可执行化）
import re
core_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workflow_base", "core")
domain_words = ["小智", "xiaozhi", "攻防", "黑客", "家电维修", "机械臂", "水下机器人"]
violations = []
for fn in os.listdir(core_dir):
    if not fn.endswith(".py"):
        continue
    p = os.path.join(core_dir, fn)
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()
    for w in domain_words:
        if w in text:
            violations.append({"file": fn, "word": w})
report["sections"].append({"section": "core_domain_word_check", "violations": violations, "pass": not violations})

report["all_pass"] = (
    reserved_check["pass"]
    and final["status"] in ("成功", "失败")
    and selfcheck["all_pass"]
    and not violations
)

path = out_json("verify_base_2026-11-10.json", report)
print(json.dumps({"written": path, "all_pass": report["all_pass"]}, ensure_ascii=False))