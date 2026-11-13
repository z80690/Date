"""实例与任务调度器（任务 2.3/2.4）。

受理链五道校验、全局唯一任务标识、手动重查；
回执驱动五取值状态机：仅回执可触发 执行中→成功/失败，仅断连检测可触发→中断。
"""

from __future__ import annotations

import threading
import uuid
from typing import Any, Callable, Dict, List, Optional

STATUS_PENDING = "待启动"
STATUS_RUNNING = "执行中"
STATUS_SUCCESS = "成功"
STATUS_FAILED = "失败"
STATUS_INTERRUPTED = "中断"
VALID_STATUSES = (STATUS_PENDING, STATUS_RUNNING, STATUS_SUCCESS, STATUS_FAILED, STATUS_INTERRUPTED)


class SchedulerError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class Scheduler:
    def __init__(self, store, catalog_registry, object_registry, security, translator):
        self._store = store
        self._catalogs = catalog_registry
        self._objects = object_registry
        self._security = security
        self._translator = translator
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._rechecks: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = threading.RLock()
        saved = store.load("instances")
        if saved:
            for tid, t in saved.items():
                if t["status"] in (STATUS_PENDING, STATUS_RUNNING):
                    t["status"] = STATUS_INTERRUPTED
                    t["reason"] = "底座重启，执行中任务不恢复，标记中断"
                self._tasks[tid] = t
        self._notifier: Optional[Callable[[Dict[str, Any]], None]] = None

    def set_notifier(self, fn: Callable[[Dict[str, Any]], None]) -> None:
        self._notifier = fn

    def _persist(self) -> None:
        self._store.save("instances", self._tasks)

    def _notify(self, event: Dict[str, Any]) -> None:
        if self._notifier:
            self._notifier(event)

    def start_task(self, catalog_id: str, object_id: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            self._catalogs.require_implemented(catalog_id)
            obj = self._objects.get(object_id)
            if not obj:
                raise SchedulerError(
                    "OBJECT_NOT_REGISTERED",
                    f"任务指向未注册对象: {object_id}；已拒绝，零执行侧动作",
                )
            if obj["catalog_id"] != catalog_id:
                raise SchedulerError(
                    "CATALOG_MISMATCH",
                    f"对象 {object_id} 不属于类目 {catalog_id}",
                )
            if obj["status"] != "online":
                raise SchedulerError(
                    "OBJECT_OFFLINE",
                    f"对象当前状态: {obj['status']}；离线拒绝受理，不做排队与重投",
                )
            capabilities = obj["capability"]["actions"]
            matched = next((a for a in capabilities if a["name"] == action), None)
            if not matched:
                names = [a["name"] for a in capabilities]
                raise SchedulerError(
                    "ACTION_OUT_OF_SCOPE",
                    f"动作越界: {action} 不在能力声明内；该对象能力清单: {names}",
                )
            verdict = self._security.check_task(catalog_id, object_id, action, params)
            if not verdict["allowed"]:
                raise SchedulerError(verdict["code"], verdict["message"])

            task_id = uuid.uuid4().hex
            task = {
                "task_id": task_id,
                "catalog_id": catalog_id,
                "object_id": object_id,
                "action": action,
                "params": params,
                "status": STATUS_PENDING,
                "reason": "",
                "events": [],
            }
            self._tasks[task_id] = task
            try:
                translated = self._translator(catalog_id, object_id, action, params)
            except Exception as exc:
                task["status"] = STATUS_FAILED
                task["reason"] = f"适配翻译失败: {exc}"
                self._persist()
                self._notify({"event": "task_failed", "task_id": task_id, "reason": task["reason"]})
                return task
            task["status"] = STATUS_RUNNING
            task["dispatch"] = translated
            self._persist()
            self._store.append_event(
                {"event": "task_started", "task_id": task_id, "action": action}
            )
            return task

    def query(self, task_id: str) -> Dict[str, Any]:
        task = self._tasks.get(task_id)
        if not task:
            raise SchedulerError("TASK_NOT_FOUND", f"任务不存在: {task_id}")
        return dict(task)

    def recheck(self, task_id: str) -> Dict[str, Any]:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise SchedulerError("TASK_NOT_FOUND", f"任务不存在: {task_id}")
            events = list(task["events"])
            record = {
                "recheck_at_count": len(events),
                "status_seen": task["status"],
                "note": "",
            }
            if task["status"] == STATUS_RUNNING and not events:
                record["note"] = "回执缺失：尚未收到任何回执，状态保持执行中"
            elif task["status"] == STATUS_RUNNING:
                record["note"] = "已收到部分回执，任务仍在执行中"
            self._rechecks.setdefault(task_id, []).append(record)
            return {"task": dict(task), "rechecks": list(self._rechecks[task_id])}

    def apply_receipt(self, receipt: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            task_id = receipt["task_id"]
            task = self._tasks.get(task_id)
            if not task:
                self._notify(
                    {"event": "orphan_receipt", "task_id": task_id, "note": "孤儿回执：无关联任务，不驱动任何状态"}
                )
                return {"accepted": False, "orphan": True}
            if task["status"] != STATUS_RUNNING:
                self._notify(
                    {"event": "late_receipt", "task_id": task_id, "status": task["status"]}
                )
                return {"accepted": False, "note": f"任务状态为 {task['status']}，回执不再驱动状态"}
            seq = len(task["events"]) + 1
            entry = {"seq": seq, "receipt": receipt}
            task["events"].append(entry)
            terminal = receipt.get("terminal", True)
            if terminal:
                if receipt["conclusion"] == "成功":
                    task["status"] = STATUS_SUCCESS
                    task["reason"] = ""
                elif receipt["conclusion"] == "失败":
                    task["status"] = STATUS_FAILED
                    task["reason"] = receipt.get("detail") or "回执结论为失败（未附详细原因）"
            self._persist()
            self._notify({"event": "result_event", "task_id": task_id, "seq": seq, "conclusion": receipt["conclusion"], "terminal": terminal})
            return {"accepted": True, "seq": seq, "status": task["status"]}

    def mark_interrupted(self, object_id: str, reason: str) -> List[str]:
        with self._lock:
            hit = []
            for tid, task in self._tasks.items():
                if task["object_id"] == object_id and task["status"] in (STATUS_PENDING, STATUS_RUNNING):
                    task["status"] = STATUS_INTERRUPTED
                    task["reason"] = reason
                    hit.append(tid)
                    self._notify({"event": "task_interrupted", "task_id": tid, "reason": reason})
            self._persist()
            return hit

    def all_tasks(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {k: dict(v) for k, v in self._tasks.items()}