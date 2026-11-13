"""门禁管理器（任务 2.10）。

三取值状态机（等待确认/已同意/已驳回）、越阶段请求拒绝、
驳回意见原文记录与修订重提（期间阶段不推进）（spec 5.6、6.6）。
"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List, Optional

WAITING = "等待确认"
APPROVED = "已同意"
REJECTED = "已驳回"

STAGE_ORDER = ["spec", "design", "tasks", "eval_reports", "execution", "acceptance"]


class GateError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class GateManager:
    def __init__(self, store):
        self._store = store
        self._gates: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        saved = store.load("gates")
        if saved:
            self._gates = saved

    def _persist(self) -> None:
        self._store.save("gates", self._gates)

    def submit(self, stage: str, artifact_ref: str, allowed_after: Optional[str] = None) -> Dict[str, Any]:
        with self._lock:
            if allowed_after:
                idx_now = STAGE_ORDER.index(stage)
                idx_allow = STAGE_ORDER.index(allowed_after)
                if idx_now > idx_allow + 1:
                    raise GateError(
                        "STAGE_SKIPPED",
                        f"越阶段请求被拒: {stage} 不能越过 {allowed_after} 提交（5.6.3 异常 1）",
                    )
            existing = self._gates.get(stage)
            if existing and existing["status"] == APPROVED:
                return {"stage": stage, "status": APPROVED, "note": "该阶段已同意，无需重复提交"}
            record = {
                "stage": stage,
                "artifact_ref": artifact_ref,
                "status": WAITING,
                "reject_opinion": "",
                "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "decided_at": "",
                "history": [],
            }
            if existing:
                record["history"] = existing.get("history", []) + [existing]
            self._gates[stage] = record
            self._persist()
            return {"stage": stage, "status": WAITING, "artifact_ref": artifact_ref}

    def confirm(self, stage: str) -> Dict[str, Any]:
        with self._lock:
            gate = self._gates.get(stage)
            if not gate:
                raise GateError("NOT_FOUND", f"门禁不存在: {stage}")
            gate["status"] = APPROVED
            gate["decided_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            self._persist()
            return {"stage": stage, "status": APPROVED}

    def reject(self, stage: str, opinion: str) -> Dict[str, Any]:
        with self._lock:
            gate = self._gates.get(stage)
            if not gate:
                raise GateError("NOT_FOUND", f"门禁不存在: {stage}")
            gate["status"] = REJECTED
            gate["reject_opinion"] = opinion
            gate["decided_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            self._persist()
            return {"stage": stage, "status": REJECTED, "opinion": opinion, "note": "阶段不推进，须按意见修订后重提（5.6.1 规则 4）"}

    def is_approved(self, stage: str) -> bool:
        with self._lock:
            gate = self._gates.get(stage)
            return bool(gate and gate["status"] == APPROVED)

    def require_approved(self, stage: str) -> None:
        with self._lock:
            gate = self._gates.get(stage)
            if not gate or gate["status"] != APPROVED:
                raise GateError(
                    "GATE_NOT_APPROVED",
                    f"阶段 {stage} 未获用户同意，禁止推进（5.6.1 规则 1）",
                )

    def all(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {k: dict(v) for k, v in self._gates.items()}