"""嵌入式开工三自检：编译能用 / 仿真能加载 / 日志能落盘。

纯 stdlib，不依赖项目其他模块。任何一项没过就明确返回 unavailable，
绝不拿"文件存在"冒充"能跑"。所有结论来自真跑命令 + 真实退出码。

用法：
    python workspace/06_开发工具/embedded/toolchain_preflight.py
退出码：0 = 三项全过；1 = 至少一项没过。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

__all__ = ["VELXIO_HOME", "check_compile", "check_simulate", "check_log", "run_preflight"]

# 工具装在项目外 D:/refs/velxio（历史 P11/P12 落地，只读参考，不进 git）
VELXIO_HOME = "D:/refs/velxio"
CLI = VELXIO_HOME + "/tools/arduino-cli.exe"
SIM_TEST = VELXIO_HOME + "/frontend/src/__tests__/AVRSimulator.test.ts"
VITEST = VELXIO_HOME + "/frontend/node_modules/.bin/vitest.cmd"


def _probe(name: str, path: str) -> dict[str, Any]:
    return {"item": name, "path": path, "pass": os.path.exists(path)}


def check_compile() -> dict[str, Any]:
    """编译能力：工具在不在 + 芯片包装没装 + 版本命令真跑通没。"""
    checks = [_probe("arduino-cli", CLI)]
    if not os.path.exists(CLI):
        return {"ready": False, "checks": checks, "reason": "编译器文件不在"}
    try:
        ver = subprocess.run([CLI, "version"], capture_output=True, text=True, timeout=30)
        core = subprocess.run([CLI, "core", "list"], capture_output=True, text=True, timeout=30)
        ver_ok = ver.returncode == 0 and "arduino-cli" in (ver.stdout or "")
        core_ok = core.returncode == 0 and "arduino:avr" in (core.stdout or "")
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ready": False, "checks": checks, "reason": f"命令没跑起来：{exc}"}
    checks.append({"item": "version 命令", "pass": ver_ok, "output": (ver.stdout or "").strip()[:200]})
    checks.append({"item": "avr 芯片包", "pass": core_ok, "output": (core.stdout or "").strip()[:200]})
    ok = ver_ok and core_ok
    return {"ready": ok, "checks": checks, "reason": None if ok else "编译层没过"}


def check_simulate() -> dict[str, Any]:
    """仿真能力：仿真内核源码 + 测试文件 + 测试跑通（真跑，不靠猜）。"""
    checks = [_probe("仿真内核源码", VELXIO_HOME + "/frontend/src/simulation/AVRSimulator.ts"),
              _probe("内核测试文件", SIM_TEST), _probe("测试执行器", VITEST)]
    if not all(c["pass"] for c in checks):
        return {"ready": False, "checks": checks, "reason": "仿真相关文件缺"}
    try:
        # bash 在 Git Bash 下调 .cmd 需要 cmd /c；直接调 node_modules 的 js 入口更稳
        proc = subprocess.run(
            ["cmd", "/c", VITEST, "run", "src/__tests__/AVRSimulator.test.ts"],
            capture_output=True, text=True, timeout=180,
            cwd=VELXIO_HOME + "/frontend",
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        test_ok = proc.returncode == 0 and "failed" not in out.lower().split("tests")[0][-40:]
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ready": False, "checks": checks, "reason": f"测试没跑起来：{exc}"}
    tail = "\n".join(out.strip().splitlines()[-6:])[:400]
    checks.append({"item": "内核单测真跑", "pass": proc.returncode == 0,
                   "exit": proc.returncode, "output": tail})
    ok = proc.returncode == 0
    return {"ready": ok, "checks": checks, "reason": None if ok else "仿真内核单测没过", "test_ok": test_ok}


def check_log() -> dict[str, Any]:
    """日志能力：能不能真的写一个文件到磁盘再读回来。"""
    target = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))), "log", "_preflight_write_test.tmp")
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        stamp = datetime.now(timezone.utc).isoformat()
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(stamp)
        with open(target, "r", encoding="utf-8") as fh:
            readback = fh.read()
        os.remove(target)
        ok = readback == stamp
    except OSError as exc:
        return {"ready": False, "path": target, "reason": f"写盘失败：{exc}"}
    return {"ready": ok, "path": target, "reason": None if ok else "读回内容不一致"}


def run_preflight() -> dict[str, Any]:
    """三项全跑，返回结构化结论；不吞错、不假绿。"""
    result = {
        "time": datetime.now(timezone.utc).isoformat(),
        "compile": check_compile(),
        "simulate": check_simulate(),
        "log": check_log(),
    }
    result["all_ready"] = all(result[k]["ready"] for k in ("compile", "simulate", "log"))
    result["verdict"] = "READY" if result["all_ready"] else "NOT READY"
    return result


if __name__ == "__main__":
    report = run_preflight()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # 落盘留痕（写进 log，不污染项目源码）
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))), "log", "embedded-preflight-latest.json")
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
        print(f"PREFLIGHT_LOG={log_path}")
    except OSError as exc:
        print(f"PREFLIGHT_LOG_WRITE_FAILED={exc}", file=sys.stderr)
    sys.exit(0 if report["all_ready"] else 1)
