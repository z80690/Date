"""试错与止损规矩：机器判定（规矩层第 10 条）。

检查四件事，全过 exit 0：
1. 两个规矩目录的第 10 条都在，且逐字一致（真加载层 + WorkBuddy 权威层不打架）
2. 第 10 条含四个失败分类 + 退避 + checkpoint + 绝对截止 + 次数仅保险（语义关键点齐全）
3. 用户级 / 项目级记忆都指向规矩层，不再残留旧的"固定3次就判死"表述
4. 用户级记忆里 attempt_budget.py 的虚假声明已清除

纯 stdlib。用法：python .workbuddy/scripts/retry_policy_check.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DATE_ROOT = os.path.dirname(os.path.dirname(HERE))
USER_HOME = os.path.expanduser("~")

RULES = [
    os.path.join(DATE_ROOT, ".codebuddy", "rules", "项目工作规则.md"),
    os.path.join(DATE_ROOT, ".workbuddy", "rules", "项目工作规则.md"),
]
USER_MEM = os.path.join(
    USER_HOME, ".workbuddy",
    "user-52545793-2661-4f72-98cf-6c28a317dbab-personal", "MEMORY.md",
)
PROJ_MEM = os.path.join(DATE_ROOT, ".workbuddy", "memory", "MEMORY.md")

# 第 10 条必须命中的语义关键点（大白话关键词，防写歪）
KEY_POINTS = {
    "外部故障重派": ("外部故障", "重派"),
    "预算耗尽断点续": ("预算耗尽", "断点"),
    "exhausted 不算失败": ("exhausted", "不算失败"),
    "跑完没成禁原样重派": ("禁止原样重派",),
    "同处卡住换方向": ("换方向",),
    "退避翻倍封顶": ("退避", "封顶"),
    "失败落盘checkpoint": ("落盘", "停在哪一步"),
    "绝对截止时间": ("绝对截止时间",),
    "次数仅最后保险": ("保险",),
}


def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def _rule10(text: str) -> str:
    for line in text.splitlines():
        if line.strip().startswith("10. 试错与止损"):
            return line.strip()
    return ""


def check() -> dict:
    checks: list[dict] = []
    bodies = [_read(p) for p in RULES]
    r10 = [_rule10(b) for b in bodies]

    for path, body in zip(RULES, r10):
        checks.append({
            "item": f"规矩层第10条存在: {os.path.relpath(path, DATE_ROOT)}",
            "pass": bool(body),
        })

    if r10[0] and r10[1]:
        checks.append({
            "item": "两处规矩第10条逐字一致（不打架）",
            "pass": r10[0] == r10[1],
        })
    else:
        checks.append({"item": "两处规矩第10条逐字一致（不打架）", "pass": False})

    joined = r10[1] if r10[1] else ""
    for name, needles in KEY_POINTS.items():
        checks.append({
            "item": f"第10条语义点: {name}",
            "pass": all(n in joined for n in needles),
        })

    user, proj = _read(USER_MEM), _read(PROJ_MEM)
    checks.append({
        "item": "用户级记忆指向规矩层第10条",
        "pass": "规矩层第 10 条" in user and "试错与止损" in user,
    })
    checks.append({
        "item": "项目级记忆指向规矩层第10条",
        "pass": "唯一权威正文" in proj and "规矩层第 10 条" in proj,
    })
    checks.append({
        "item": "用户级记忆已清除 attempt_budget.py 虚假声明",
        "pass": "attempt_budget.py" in user and "从未存在" in user,
    })
    checks.append({
        "item": "用户级记忆不再残留旧'第4次直接拒绝'硬规则",
        "pass": "第 4 次必须**直接拒绝**" not in user,
    })

    all_pass = all(c["pass"] for c in checks)
    return {
        "time": datetime.now(timezone.utc).isoformat(),
        "all_pass": all_pass,
        "verdict": "PASS" if all_pass else "FAIL",
        "checks": checks,
    }


if __name__ == "__main__":
    report = check()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["all_pass"] else 1)
