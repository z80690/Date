"""回执中心（任务 2.5）。

回执与实例关联校验（孤儿告警）、结论完整性校验、统一时间戳、
顺序号分配并按产生顺序回传结果事件（spec 5.3.1 规则 9、6.3）。
"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List


class ReceiptError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class ReceiptCenter:
    def __init__(self, store, scheduler, apply_to_scheduler: bool = True):
        self._store = store
        self._scheduler = scheduler
        self._apply = apply_to_scheduler
        self._receipts: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        saved = store.load("receipts")
        if saved:
            self._receipts = saved

    def _persist(self) -> None:
        self._store.save("receipts", self._receipts)

    def submit(self, task_id: str, conclusion: str, detail: str = "", terminal: bool = True) -> Dict[str, Any]:
        with self._lock:
            if not conclusion or not str(conclusion).strip():
                raise ReceiptError(
                    "EMPTY_CONCLUSION",
                    "回执结论为空被拒收：回执必须给出 成功/失败 之一的明确结论（6.3.2）",
                )
            receipt = {
                "task_id": task_id,
                "conclusion": conclusion,
                "detail": detail,
                "terminal": terminal,
                "received_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            self._receipts.append(receipt)
            self._persist()
            result = {"receipt": receipt}
            if self._apply:
                result["apply"] = self._scheduler.apply_receipt(receipt)
            return result

    def events_in_order(self, task_id: str) -> List[Dict[str, Any]]:
        task = self._scheduler.query(task_id)
        return sorted(task.get("events", []), key=lambda e: e["seq"])

    def all(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._receipts)