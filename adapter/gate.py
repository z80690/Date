"""IF-7 learn-gate release check (design.md 2.2.2, spec 5.2.1-2/3/4/5)."""

from __future__ import annotations

from adapter import storage
from adapter.config import REPO_ROOT
from adapter.errors import AdapterException, ErrorCode

_NOTES = REPO_ROOT / "notes"
_SPEC_DIR = REPO_ROOT / ".codeartsdoer" / "specs" / "20261112_P003_local_redblue_drill_baseline"

_GATE_EVIDENCE = {
    "learn_gate_l1": [_NOTES / "学习成果-三大框架官方文档.md"],
    "learn_gate_l2": [_NOTES / "学习成果-真实案例正反例.md"],
    "learn_gate_l3": [_NOTES / "学习成果-真实案例正反例.md"],
    "learn_gate_l4": [_NOTES / "学习成果-攻防框架近三月使用调研.md"],
}

_INDEX = _NOTES / "知识库索引.md"
_EXAM_REPORT = _SPEC_DIR / "exam" / "R1" / "review-report.md"
_TRACE = _SPEC_DIR / "gates" / "learn-gate-trace.md"


def gate_check(gate: str, evidence_dir=None) -> dict:
    """Verify one learn-gate tier: evidence files + KB index + exam release.

    Returns {"passed": bool, "missing_items": [...], "trace_ref": str}.
    Any missing registration maps to E_KB_NOT_REGISTERED (design.md).
    """
    if gate not in _GATE_EVIDENCE:
        raise AdapterException(ErrorCode.E_KB_NOT_REGISTERED, f"unknown gate: {gate}")

    missing: list[str] = []
    for path in _GATE_EVIDENCE[gate]:
        if not path.is_file():
            missing.append(f"evidence file missing: {path.name}")
    if _INDEX.is_file():
        index_text = _INDEX.read_text(encoding="utf-8")
        for path in _GATE_EVIDENCE[gate]:
            if path.name not in index_text:
                missing.append(f"KB index lacks entry: {path.name}")
    else:
        missing.append("KB index file missing")

    if not _EXAM_REPORT.is_file():
        missing.append("exam release report missing (exam/R1/review-report.md)")
    elif "放行" not in _EXAM_REPORT.read_text(encoding="utf-8"):
        missing.append("exam report does not grant release (confidence <80%?)")

    passed = not missing
    record = {"gate": gate, "passed": passed, "missing_items": missing}
    storage.append_record("gate", record, base_dir=evidence_dir)
    if not passed:
        raise AdapterException(
            ErrorCode.E_KB_NOT_REGISTERED,
            f"{gate} not satisfied",
            detail=record,
        )
    return {"passed": True, "missing_items": [], "trace_ref": str(_TRACE)}
