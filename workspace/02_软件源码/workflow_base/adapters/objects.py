"""对象注册与上线声明（任务 3.5）。

对象注册（能力声明三要素必填、所属类目须已挂载且已实现）、
上线声明与心跳登记（在线状态生效、环境声明进入安全校验器台账）。
"""

from __future__ import annotations

import threading
from typing import Any, Dict


class ObjectError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class ObjectRegistry:
    def __init__(self, store, catalog_registry):
        self._store = store
        self._catalogs = catalog_registry
        self._objects: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        saved = store.load("objects")
        if saved:
            self._objects = saved

    def _persist(self) -> None:
        self._store.save("objects", self._objects)

    def register(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        from .contract import validate_object_contract, ContractError

        with self._lock:
            try:
                validate_object_contract(obj)
            except ContractError as exc:
                raise ObjectError(exc.code, exc.message)
            oid = obj["object_id"]
            if oid in self._objects:
                raise ObjectError("DUPLICATE_ID", f"对象标识已存在: {oid}")
            cat = self._catalogs.get(obj["catalog_id"])
            if not cat:
                raise ObjectError("CATALOG_NOT_MOUNTED", f"所属类目未挂载: {obj['catalog_id']}")
            if cat["implementation_status"] != "implemented":
                raise ObjectError(
                    "CATALOG_RESERVED",
                    "所属类目为仅预留接口状态，对象注册被拒（5.3.1 规则 4）",
                )
            record = dict(obj)
            record["status"] = "offline"
            self._objects[oid] = record
            self._persist()
            return record

    def go_online(self, object_id: str, env_declaration: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            obj = self._objects.get(object_id)
            if not obj:
                raise ObjectError("NOT_FOUND", f"对象不存在: {object_id}")
            obj["status"] = "online"
            obj["env_declaration"] = env_declaration
            self._persist()
            return {"object_id": object_id, "status": "online"}

    def go_offline(self, object_id: str) -> Dict[str, Any]:
        with self._lock:
            obj = self._objects.get(object_id)
            if not obj:
                raise ObjectError("NOT_FOUND", f"对象不存在: {object_id}")
            obj["status"] = "offline"
            self._persist()
            return {"object_id": object_id, "status": "offline"}

    def get(self, object_id: str) -> Dict[str, Any]:
        return self._objects.get(object_id)

    def list_online(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {k: v for k, v in self._objects.items() if v.get("status") == "online"}

    def all(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return dict(self._objects)