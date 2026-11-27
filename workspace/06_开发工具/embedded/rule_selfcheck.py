"""规矩自证：E1 开工门禁 + E2 工具路径铁律 是否真落盘、真能跑。

纯 stdlib。检查三件事：
1. 项目记忆 / 用户级记忆里有没有 E1/E2 两条规矩（文本检查）
2. 专家规矩里有没有把门禁和铁律写死（文本检查）
3. 门禁指向的体检脚本真跑一次，退出码必须为 0（真跑，不信文件存在）

用法：python workspace/06_开发工具/embedded/rule_selfcheck.py
退出码：0 = 规矩都在且体检真过；1 = 至少一项缺或体检没过。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

__all__ = ["check_rules", "run_selfcheck"]

HERE = os.path.dirname(os.path.abspath(__file__))
# 四层上是 Date 项目根：embedded -> 06_开发工具 -> workspace -> Date
DATE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PROJ_MEM = os.path.join(DATE_ROOT, ".workbuddy", "memory", "MEMORY.md")
USER_HOME = os.path.expanduser("~")
USER_MEM = os.path.join(
    USER_HOME, ".workbuddy",
    "user-52545793-2661-4f72-98cf-6c28a317dbab-personal", "MEMORY.md",
)
EXPERT_MD = os.path.join(
    USER_HOME, ".workbuddy", "plugins", "marketplaces", "my-experts",
    "plugins", "embedded-dev", "agents", "embedded-dev.md",
)
PREFLIGHT = os.path.join(HERE, "toolchain_preflight.py")


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def check_rules() -> list[dict[str, Any]]:
    """文本层：规矩在不在该在的地方。"""
    proj, user, expert = _read(PROJ_MEM), _read(USER_MEM), _read(EXPERT_MD)
    checks = [
        {"rule": "E1", "where": "项目记忆", "pass": "E1" in proj and "toolchain_preflight.py" in proj},
        {"rule": "E1", "where": "用户记忆(跨工作区兜底)", "pass": "E1 开工门禁" in user and "toolchain_preflight.py" in user},
        {"rule": "E2", "where": "项目记忆", "pass": "E2" in proj and "PATH" in proj},
        {"rule": "E2", "where": "用户记忆(跨工作区兜底)", "pass": "E2 路径实情" in user and "D:/refs/velxio" in user},
        {"rule": "E1", "where": "专家规矩", "pass": "E1" in expert and "toolchain_preflight.py" in expert},
        {"rule": "E2", "where": "专家规矩", "pass": "E2 铁律" in expert and "D:/refs/velxio" in expert},
    ]
    return checks


def run_selfcheck() -> dict[str, Any]:
    checks = check_rules()
    try:
        proc = subprocess.run(
            [sys.executable, PREFLIGHT], capture_output=True, text=True,
            timeout=300, cwd=DATE_ROOT,
        )
        gate = {"rule": "E1", "where": "体检真跑", "pass": proc.returncode == 0,
                "exit": proc.returncode}
    except (OSError, subprocess.SubprocessError) as exc:
        gate = {"rule": "E1", "where": "体检真跑", "pass": False, "reason": str(exc)}
    checks.append(gate)
    return {
        "time": datetime.now(timezone.utc).isoformat(),
        "all_pass": all(c["pass"] for c in checks),
        "verdict": "PASS" if all(c["pass"] for c in checks) else "FAIL",
        "checks": checks,
    }


if __name__ == "__main__":
    report = run_selfcheck()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["all_pass"] else 1)
