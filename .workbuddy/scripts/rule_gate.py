"""规则合规门禁：机器判，exit code 可判（0=全绿，非0=有红项）。

检查四件事：
  C1 两份规则 md5 == 基线（.workbuddy 权威源 + .codebuddy 注入源）
  C2 两个 runtime 副本内容一致（防单侧被改）
  C3 两个子智能体定义含"开工先读规则全文"硬步骤（否则规则进不了它上下文）
  C4 功能隔离：.workbuddy 运行时文件不把 .codeartsdoer 写成依赖

用法：
  python rule_gate.py            # 跑门禁，全绿 exit 0
  python rule_gate.py --context  # 打印两份规则正文（派工时粘进子智能体 prompt）
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

__all__ = ["BASELINE", "check", "emit_context", "main"]

ROOT = Path(__file__).resolve().parents[2]
W_RULES = ROOT / ".workbuddy" / "rules"
B_RULES = ROOT / ".codebuddy" / "rules"
AGENTS = ROOT / ".workbuddy" / "agents"

COVENANT = "项目协作公约.md"
SOP = "项目工作规则.md"

BASELINE = {
    COVENANT: "417ce361f7ab46a5a0088c555bb4a843",
    SOP: "a1b72db2e6491a4dec9805b07d8c17d7",
}

AGENT_READ_MARK = "开工先读规则全文"
ISOLATION_FORBIDDEN = ("依赖 .codeartsdoer", "依赖`.codeartsdoer", "运行时读取 .codeartsdoer")


def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _check_md5(results: list[tuple[str, bool, str]]) -> None:
    for name, want in BASELINE.items():
        for label, base in ((".workbuddy", W_RULES), (".codebuddy", B_RULES)):
            p = base / name
            got = _md5(p) if p.is_file() else "MISSING"
            results.append((f"C1 {label}/{name} md5", got == want, f"want={want} got={got}"))


def _check_copy_equal(results: list[tuple[str, bool, str]]) -> None:
    for name in BASELINE:
        a, b = W_RULES / name, B_RULES / name
        same = a.is_file() and b.is_file() and a.read_bytes() == b.read_bytes()
        results.append((f"C2 副本一致 {name}", same, "两目录字节一致" if same else "副本不一致或缺失"))


def _check_agents(results: list[tuple[str, bool, str]]) -> None:
    for name in ("sdd-examiner.md", "sdd-grader.md"):
        p = AGENTS / name
        ok = p.is_file() and AGENT_READ_MARK in p.read_text(encoding="utf-8")
        results.append((f"C3 {name} 读规则步骤", ok, "含开工先读规则" if ok else "缺读规则硬步骤"))


def _check_isolation(results: list[tuple[str, bool, str]]) -> None:
    bad: list[str] = []
    for p in (ROOT / ".workbuddy").rglob("*.md"):
        text = p.read_text(encoding="utf-8")
        for token in ISOLATION_FORBIDDEN:
            if token in text:
                bad.append(f"{p.name}:{token}")
    results.append(("C4 功能隔离", not bad, "无跨侧依赖" if not bad else ";".join(bad)))


def check() -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []
    _check_md5(results)
    _check_copy_equal(results)
    _check_agents(results)
    _check_isolation(results)
    return results


def emit_context() -> None:
    for name in (COVENANT, SOP):
        p = W_RULES / name
        print(f"===== {name} =====")
        print(p.read_text(encoding="utf-8") if p.is_file() else "MISSING")


def main() -> int:
    if "--context" in sys.argv:
        emit_context()
        return 0
    results = check()
    for label, ok, detail in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {label} :: {detail}")
    red = [r for r in results if not r[1]]
    print(f"\n{'ALL GREEN' if not red else 'GATE RED'} — {len(results) - len(red)}/{len(results)} passed")
    return 0 if not red else 1


if __name__ == "__main__":
    raise SystemExit(main())
