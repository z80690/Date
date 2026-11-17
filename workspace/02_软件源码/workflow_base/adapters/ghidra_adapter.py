"""Ghidra 二进制逆向适配层（纯 stdlib）。

来源：P17（2026-11-17）。用户要求集成"AI 逆向二进制"能力（头条视频指向 IDA 9.5）。
选型依据（预测校正，多独立来源）：
- 视频标题 + Hex-Rays 官方博客实锤：IDA 9.5 AI = 官方 MCP(MIT) + Assist，
  但 IDA 本体商业授权（$365/年起），视频教程路线为安装+汉化（社区破解），
  不采用，不装破解版；
- Ghidra 11.3.2（NSA 开源 BSD，业界事实标准）支持本机 JDK 17，作为对等逆向核心；
- AI 解释层同 GhidraMCP/OGhidra 思路走 LLM 桥，本层先做无头静态反编译底座。
设计纪律（同 velxio_adapter，对应用户第七条"预测校正"）：
- 先探测真实环境再报状态；依赖缺失返回 unavailable + 原因，绝不假装就绪。
- 不改 Ghidra 任何源码，只做薄封装 + 无头调用 + 结果归一。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from typing import Any

# 默认落地位置（P17 下载到 D:/refs，项目外，符合"仓库存项目外"约定）
# 实测注记（2026-11-17）：Ghidra 11.3.2 的 application.properties 明确
# application.java.min=21 —— 需要 JDK 21；本机 PATH 上的 java 是 17，不够。
# 因此适配层要求一个独立 JDK21 绿色包（D:/refs/jdk21），启动时单独指给它。
DEFAULT_GHIDRA_HOME = "D:/refs/ghidra_11.3.2_PUBLIC"
DEFAULT_JDK21_HOME = "D:/refs/jdk21"
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "ghidra_scripts")
DUMP_TIMEOUT_SECONDS = 900
DEFAULT_MAX_FUNCTIONS = 40

__all__ = [
    "DEFAULT_GHIDRA_HOME",
    "DEFAULT_JDK21_HOME",
    "SCRIPTS_DIR",
    "detect",
    "analyze_binary",
    "normalize_dump",
    "capability",
]


def _check_headless(ghidra_home: str, checks: list[dict[str, Any]]) -> str | None:
    headless = os.path.join(ghidra_home, "support", "analyzeHeadless.bat")
    ok = os.path.exists(headless)
    checks.append({"item": "analyzeHeadless", "path": headless, "pass": ok})
    return headless if ok else None


def _check_jdk(jdk21_home: str, checks: list[dict[str, Any]]) -> str | None:
    java = os.path.join(jdk21_home, "bin", "java.exe")
    ok = os.path.exists(java)
    checks.append({"item": "jdk21", "path": java, "pass": ok})
    if not ok:
        path_java = shutil.which("java")
        checks.append({
            "item": "java(PATH)", "path": path_java or "未找到",
            "pass": False,
            "note": "PATH 上的 java 版本须为 21+；Ghidra 11.3.2 要求 JDK21（java.min=21）",
        })
    return jdk21_home if ok else None


def _read_version(ghidra_home: str) -> str | None:
    props = os.path.join(ghidra_home, "Ghidra", "application.properties")
    if not os.path.exists(props):
        return None
    with open(props, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("application.version="):
                return line.strip().split("=", 1)[1]
    return None


def detect(ghidra_home: str = DEFAULT_GHIDRA_HOME,
           jdk21_home: str = DEFAULT_JDK21_HOME) -> dict[str, Any]:
    """探测 Ghidra 是否真能用。逐项查真实文件，返回结构化结论。

    不靠目录存在推断"能跑"——analyzeHeadless.bat 或 JDK21 缺一个都不算就绪。
    """
    checks: list[dict[str, Any]] = []
    headless = _check_headless(ghidra_home, checks)
    jdk_home = _check_jdk(jdk21_home, checks)
    version = _read_version(ghidra_home)
    all_ok = headless is not None and jdk_home is not None
    return {
        "status": "ready" if all_ok else "unavailable",
        "ready": all_ok,
        "headless": headless,
        "jdk_home": jdk_home,
        "home": ghidra_home,
        "version": version,
        "checks": checks,
        "reason": None if all_ok else "环境未就绪：缺少上表中的失败项（不假装可用）",
    }


def normalize_dump(payload: dict[str, Any]) -> dict[str, Any]:
    """把无头导出的函数清单归一成稳定结构（纯函数，机器无关，可单测）。"""
    funcs = []
    for f in payload.get("functions", []):
        funcs.append({
            "name": f.get("name"),
            "entry": f.get("entry"),
            "size_bytes": f.get("size_bytes"),
            "decompiled": bool(f.get("decompiled_c")),
        })
    return {
        "program": payload.get("program"),
        "language_id": payload.get("language_id"),
        "function_count": payload.get("function_count", len(funcs)),
        "decompiled_count": sum(1 for f in funcs if f["decompiled"]),
        "functions": funcs,
    }


def _stage_scripts(proj_dir: str) -> str:
    """把导出脚本拷到项目目录（ASCII 路径）再指给 Ghidra。

    实测注记：Jython 2.7 PyString 不接受非 ASCII 路径，仓库目录含中文
    （02_软件源码）会让 postScript 直接崩；拷到工作目录绕开，仓库源文件不动。
    """
    dst = os.path.join(proj_dir, "ghidra_scripts")
    os.makedirs(dst, exist_ok=True)
    shutil.copyfile(os.path.join(SCRIPTS_DIR, "dump_functions.py"),
                    os.path.join(dst, "dump_functions.py"))
    return dst


def _run_headless(headless: str, binary_path: str, proj_dir: str, out_json: str,
                  max_functions: int, timeout: int,
                  jdk_home: str | None) -> subprocess.CompletedProcess:
    cmd = [
        headless, proj_dir, "DateP17", "-import", os.path.abspath(binary_path),
        "-scriptPath", _stage_scripts(proj_dir),
        "-postScript", "dump_functions.py", out_json, str(max_functions),
        "-deleteProject",
    ]
    env = os.environ.copy()
    if jdk_home:
        env["JAVA_HOME"] = jdk_home  # 只给 Ghidra 子进程指 JDK21，不动全局
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)


def _analyze_ready(d: dict[str, Any], binary_path: str, work_dir: str | None,
                   max_functions: int, timeout: int) -> dict[str, Any]:
    if not os.path.exists(binary_path):
        return {"status": "error", "ok": False,
                "reason": f"目标二进制不存在: {binary_path}", "detect": d}
    proj_dir = work_dir or tempfile.mkdtemp(prefix="ghidra_p17_")
    os.makedirs(proj_dir, exist_ok=True)
    out_json = os.path.join(proj_dir, "dump_functions.json")
    try:
        proc = _run_headless(d["headless"], binary_path, proj_dir,
                             out_json, max_functions, timeout, d["jdk_home"])
    except subprocess.TimeoutExpired:
        return {"status": "failed", "ok": False,
                "reason": f"无头分析超时({timeout}s)", "detect": d}
    except Exception as exc:  # noqa: BLE001 - 调用失败如实报错
        return {"status": "error", "ok": False, "reason": str(exc), "detect": d}
    if os.path.exists(out_json):
        with open(out_json, encoding="utf-8", errors="replace") as fh:
            dump = json.load(fh)
        return {"status": "verified", "ok": True,
                "result": normalize_dump(dump), "raw_dump_path": out_json,
                "project_dir": proj_dir, "detect": d}
    tail = (proc.stdout or "")[-1500:] + (proc.stderr or "")[-800:]
    return {"status": "failed", "ok": False,
            "reason": "无头分析未产出导出文件（不假装成功）",
            "output_tail": tail, "detect": d}


def analyze_binary(binary_path: str, ghidra_home: str = DEFAULT_GHIDRA_HOME,
                   work_dir: str | None = None,
                   max_functions: int = DEFAULT_MAX_FUNCTIONS,
                   timeout: int = DUMP_TIMEOUT_SECONDS) -> dict[str, Any]:
    """无头导入+分析目标二进制，导出函数清单与反编译 C 代码。

    只做静态只读分析，不执行目标程序本体。
    """
    d = detect(ghidra_home)
    if not d["ready"]:
        return {"status": "unavailable", "ok": False, "reason": d["reason"], "detect": d}
    return _analyze_ready(d, binary_path, work_dir, max_functions, timeout)


def capability(ghidra_home: str = DEFAULT_GHIDRA_HOME) -> dict[str, Any]:
    """返回本适配层提供的能力声明（供 catalog / 调用点读取）。"""
    d = detect(ghidra_home)
    return {
        "name": "ghidra_reverse",
        "tier": "binary-reverse-engineering",
        "selection": {
            "video_pointer": "IDA 9.5（商业授权+汉化破解路线，不采用）",
            "chosen": "Ghidra 11.3.2（NSA 开源 BSD，本机 JDK 17 可跑）",
        },
        "runtime": d,
        "mcp_tools": ["analyze_binary"],
        "not_yet_verified": ["AI 解释层(LLM 桥)", "GhidraMCP 集成", "批量多二进制流水"],
    }


if __name__ == "__main__":
    print(json.dumps(capability(), ensure_ascii=False, indent=2))
