"""SDD 四步产物自检（spec.md v1.0 / design.md v1.0 / tasks.md v1.0）。

按 STEP_FILES 检查四步落盘文件是否齐全且非空。
退出码：0=全绿(4/4)，1=有缺失，2=参数或路径错误。
纯标准库，无定时器、无轮询（公约第 5 条）。
"""

from __future__ import annotations

import sys
from pathlib import Path

__all__ = ["STEP_FILES", "check", "main"]

STEP_FILES = (
    (1, "spec.md"),
    (2, "design.md"),
    (3, "tasks.md"),
    (4, "apply_record.md"),
)


def check(target: Path) -> list[tuple[int, str, bool]]:
    """返回 [(步骤号, 文件名, 是否存在且非空), ...]。"""
    result = []
    for step, name in STEP_FILES:
        p = target / name
        ok = p.is_file() and p.stat().st_size > 0
        result.append((step, name, ok))
    return result


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python sdd_check.py <SDD目录路径>")
        return 2
    target = Path(sys.argv[1])
    if not target.is_dir():
        print(f"FAIL: 目录不存在或不是目录: {target}")
        return 2
    result = check(target)
    missing = [(s, n) for s, n, ok in result if not ok]
    for step, name, ok in result:
        print(f"[{'OK' if ok else 'MISS'}] 第{step}步 -> {name}")
    if missing:
        print(f"FAIL: 缺 {len(missing)} 项: " + ", ".join(f"第{s}步{n}" for s, n in missing))
        return 1
    print(f"PASS: {len(result)}/{len(result)} 四步产物齐全")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
