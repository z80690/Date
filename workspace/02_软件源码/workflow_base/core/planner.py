"""规划建议注入与越权剥离（任务 2.11）。

模型规划建议专用入口：单向、无执行侧副作用；入口即剥离直接执行动作，
仅保留规划语义进入待确认规划池；经用户确认后转标准调度；
回执与预期不符以回执为准并标记差异（spec 5.7.1 规则 1、5.7.3 异常 1/2）。
"""

from __future__ import annotations

import threading
import uuid
from typing import Any, Callable, Dict, List, Optional

_ACTION_VERBS = ("执行", "下发", "删除", "写入", "运行", "调用", "烧录", "重启")


class PlannerError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class Planner:
    def __init__(self, scheduler, on_confirm: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None):
        self._scheduler = scheduler
        self._on_confirm = on_confirm
        self._pool: Dict[str, Dict[str, Any]] = {}
        self._confirmed: List[Dict[str, Any]] = []
        self._lock = threading.RLock()

    def inject(self, advice_text: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        with self._lock:
            plan_id = uuid.uuid4().hex
            stripped: List[Dict[str, Any]] = []
            kept: List[Dict[str, Any]] = []
            for a in actions:
                verb = str(a.get("verb", "")).strip()
                if verb in _ACTION_VERBS:
                    stripped.append(a)
                else:
                    kept.append(a)
            plan = {
                "plan_id": plan_id,
                "advice_text": advice_text,
                "planning_semantics": kept,
                "stripped_actions": stripped,
                "status": "待确认",
                "diff_note": "",
            }
            if stripped:
                plan["diff_note"] = (
                    f"已剥离 {len(stripped)} 项直接执行动作（动词命中: "
                    + "/".join(sorted({s['verb'] for s in stripped}))
                    + "）；仅规划语义进入待确认规划池（5.7.3 异常 1）"
                )
            self._pool[plan_id] = plan
            return plan

    def confirm(self, plan_id: str) -> Dict[str, Any]:
        with self._lock:
            plan = self._pool.get(plan_id)
            if not plan:
                raise PlannerError("NOT_FOUND", f"规划不存在: {plan_id}")
            plan["status"] = "已确认"
            self._confirmed.append(plan)
            dispatched: List[Dict[str, Any]] = []
            if self._on_confirm:
                for sem in plan["planning_semantics"]:
                    dispatched.append(self._on_confirm(sem))
            return {"plan_id": plan_id, "status": "已确认", "dispatched": dispatched}

    def compare_with_receipt(self, plan_id: str, receipt_conclusion: str, receipt_detail: str) -> Dict[str, Any]:
        plan = self._pool.get(plan_id)
        if not plan:
            raise PlannerError("NOT_FOUND", f"规划不存在: {plan_id}")
        expected = plan.get("expected_conclusion", "")
        result = {
            "plan_id": plan_id,
            "expected": expected,
            "receipt_conclusion": receipt_conclusion,
            "receipt_detail": receipt_detail,
            "authoritative": "回执",
        }
        if expected and receipt_conclusion != expected:
            result["diff_marked"] = True
            result["note"] = "回执与规划预期不符：状态以回执为准，差异已标记（5.7.3 异常 2）"
        else:
            result["diff_marked"] = False
            result["note"] = "回执与规划一致或无预期声明，以回执为准"
        return result

    def pool(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {k: dict(v) for k, v in self._pool.items()}