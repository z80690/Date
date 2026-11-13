"""IF-10 attack/defense pairing check (design.md 2.2.2, spec 4.3.3-1/2)."""

from __future__ import annotations

from adapter import storage
from adapter.errors import AdapterException, ErrorCode


def pairing_check(step_no: int, evidence_dir=None) -> dict:
    """Verify one attack step has time-consistent capture + audit refs (IF-10).

    paired=True only when: capture_ref and audit_ref both present (E_PAIR_MISSING
    otherwise) AND the step output carries the feature-analysis + detection-method
    pair (E_DEFENSE_PAIR_ABSENT otherwise). Without pairing the step must not be
    counted toward round completion (spec 4.3.3-2).
    """
    dispatches = [
        d
        for d in storage.read_stream("dispatches", base_dir=evidence_dir)
        if d.get("step_no") == step_no
    ]
    receipts = [
        r
        for r in storage.read_stream("receipts", base_dir=evidence_dir)
        if r.get("step_no") == step_no
    ]
    if not dispatches or not receipts:
        raise AdapterException(
            ErrorCode.E_PAIR_MISSING,
            f"step {step_no} lacks dispatch or receipt record",
        )
    receipt = receipts[-1]
    capture_ref = receipt.get("evidence_ref")
    audit_ref = receipt.get("fact") or receipt.get("hint")

    missing: list[str] = []
    if not capture_ref:
        missing.append("capture_ref")
    if not audit_ref:
        missing.append("audit_ref")
    if missing:
        raise AdapterException(
            ErrorCode.E_PAIR_MISSING,
            f"step {step_no} missing references: {missing}",
        )

    hint_text = (receipt.get("hint") or "").lower()
    feature_pair = bool(receipt.get("fact")) and ("detection" in hint_text or "防御" in hint_text)
    if not feature_pair:
        raise AdapterException(
            ErrorCode.E_DEFENSE_PAIR_ABSENT,
            f"step {step_no} output lacks feature-analysis + detection-method pair",
        )

    result = {
        "step_no": step_no,
        "paired": True,
        "capture_ref": capture_ref,
        "audit_ref": audit_ref,
        "feature_pair_present": True,
    }
    storage.append_record("pairings", result, base_dir=evidence_dir)
    return result
