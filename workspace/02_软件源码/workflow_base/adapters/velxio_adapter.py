"""Velxio 固件仿真适配层（纯 stdlib）。

职责：把 Velxio 的固件编译/仿真能力，按工作流适配契约接进来。
设计纪律（对应用户第七条"预测校正"）：
- 先探测真实环境，再报可用与否；不靠静态推断，不假装就绪。
- 依赖缺失时返回 status=unavailable + 具体原因，绝不静默返回 True。
- 不改 Velxio 任何源码，只做薄封装 + 环境探测 + 结果归一。

Velxio 执行分两层（官方 MCP 文档明确）：
- 编译层：后端 arduino-cli 编译 sketch -> hex（本适配层可实测）
- 仿真执行层：浏览器前端加载 hex 跑指令（需在 velxio.dev 或自托管页面，本适配层不假装已完成）
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any, Dict, List, Optional

# 默认落地位置（P11 clone 到 D:/refs/velxio，项目外，符合"仓库存项目外"约定）
DEFAULT_VELXIO_HOME = "D:/refs/velxio"

# Blink 最小验证 sketch（AVR Uno，板载 LED=13）
BLINK_SKETCH = (
    "void setup() { pinMode(LED_BUILTIN, OUTPUT); }\n"
    "void loop() { digitalWrite(LED_BUILTIN, HIGH); delay(500); "
    "digitalWrite(LED_BUILTIN, LOW); delay(500); }"
)


def detect(velxio_home: str = DEFAULT_VELXIO_HOME) -> Dict[str, Any]:
    """探测 Velxio 是否真能用。逐项查真实文件，返回结构化结论。

    不靠 import 成功与否推断"能跑编译"——arduino-cli/core/venv 缺一个都不算就绪。
    """
    checks: List[Dict[str, Any]] = []

    def probe(name: str, path: str) -> bool:
        ok = os.path.exists(path)
        checks.append({"item": name, "path": path, "pass": ok})
        return ok

    cli = os.path.join(velxio_home, "tools", "arduino-cli.exe")
    venv_py = os.path.join(velxio_home, ".venv", "Scripts", "python.exe")
    verify = os.path.join(velxio_home, "verify_blink_mcp.py")

    cli_ok = probe("arduino-cli", cli)
    venv_ok = probe("venv-python", venv_py)
    verify_ok = probe("verify-script", verify)

    core_ok = False
    if cli_ok:
        try:
            out = subprocess.run(
                [cli, "core", "list"], capture_output=True, text=True, timeout=20
            )
            core_ok = "arduino:avr" in (out.stdout or "")
        except Exception as exc:  # noqa: BLE001 - 探测失败即不可用，不吞成 True
            checks.append({"item": "avr-core", "pass": False, "error": str(exc)})
        else:
            checks.append({"item": "avr-core", "pass": core_ok})

    all_ok = all(c["pass"] for c in checks)
    return {
        "status": "ready" if all_ok else "unavailable",
        "ready": all_ok,
        "home": velxio_home,
        "checks": checks,
        "reason": None if all_ok else "环境未就绪：缺少上表中的失败项（不假装可用）",
    }


def compile_blink(velxio_home: str = DEFAULT_VELXIO_HOME) -> Dict[str, Any]:
    """通过 Velxio 的 verify 脚本实编 Blink，返回归一化的实测结果。

    用子进程调 verify_blink_mcp.py（它内部调 Velxio 自带 MCP 工具），
    解析其 "VELXIO_MCP_BLINK: PASS/FAIL" 结论行。环境不具备时如实返回不可用。
    """
    d = detect(velxio_home)
    if not d["ready"]:
        return {"ok": False, "status": "unavailable", "reason": d["reason"], "detect": d}

    venv_py = os.path.join(velxio_home, ".venv", "Scripts", "python.exe")
    verify = os.path.join(velxio_home, "verify_blink_mcp.py")
    try:
        proc = subprocess.run(
            [venv_py, verify], capture_output=True, text=True, timeout=300,
            cwd=velxio_home,
        )
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": "error", "reason": str(exc), "detect": d}

    out = (proc.stdout or "") + (proc.stderr or "")
    passed = "VELXIO_MCP_BLINK: PASS" in out
    return {
        "ok": passed,
        "status": "verified" if passed else "failed",
        "returncode": proc.returncode,
        "evidence_line": next((ln for ln in out.splitlines() if "VELXIO_MCP_BLINK" in ln), None),
        "detect": d,
    }


def capability() -> Dict[str, Any]:
    """返回本适配层提供的能力声明（供 catalog / 仿真调用点读取）。"""
    d = detect()
    return {
        "name": "velxio_firmware_sim",
        "tier": "firmware-simulation",
        "protocol_layer_replaced": False,  # 协议桩保留，两层互不替代
        "runtime": d,
        "mcp_tools": ["compile_project", "run_project", "create_circuit", "update_circuit"],
        "not_yet_verified": ["浏览器前端仿真执行", "ESP32/小智固件编译加载", "Docker 镜像端到端"],
    }


if __name__ == "__main__":
    print(json.dumps(capability(), ensure_ascii=False, indent=2))
