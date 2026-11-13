"""类目注册中心（任务 2.1/2.2）。

统一挂载与校验链、类目树查询、预留状态登记、契约符合性校验。
领域无关：本模块不包含任何具体类目业务逻辑（spec 5.1.1 规则 4）。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

REQUIRED_FIELDS = (
    "catalog_id",
    "name",
    "parent_id",
    "implementation_status",
    "env_requirements",
)
VALID_STATUS = ("implemented", "reserved")
VALID_ENV = ("windows", "kali", "windows_or_kali")


class CatalogError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class CatalogRegistry:
    def __init__(self, store):
        self._store = store
        self._catalogs: Dict[str, Dict[str, Any]] = {}
        saved = store.load("catalogs")
        if saved:
            self._catalogs = saved

    def _persist(self) -> None:
        self._store.save("catalogs", self._catalogs)

    def mount(self, info: Dict[str, Any], contract_check) -> Dict[str, Any]:
        missing = [k for k in REQUIRED_FIELDS if not info.get(k)]
        if missing:
            raise CatalogError(
                "INCOMPLETE_INFO",
                "挂载信息不全，缺少字段: "
                + ", ".join(missing)
                + "；请补全上述字段后重新挂载",
            )
        if info["implementation_status"] not in VALID_STATUS:
            raise CatalogError(
                "BAD_STATUS",
                "implementation_status 仅允许: " + "/".join(VALID_STATUS),
            )
        if info["env_requirements"] not in VALID_ENV:
            raise CatalogError(
                "BAD_ENV",
                "环境要求仅允许: " + "/".join(VALID_ENV),
            )
        cid = info["catalog_id"]
        if cid in self._catalogs:
            raise CatalogError(
                "DUPLICATE_ID",
                f"类目标识已存在且不得覆盖: {cid}（重复挂载被拒绝，原类目信息保持不变）",
            )
        parent = info["parent_id"]
        if parent != "ROOT" and parent not in self._catalogs:
            raise CatalogError(
                "PARENT_MISSING",
                f"归属父类目不存在: {parent}；请先挂载父类目再挂载子类目",
            )
        contract_check(info)
        record = dict(info)
        record["extension_note"] = ""
        self._catalogs[cid] = record
        self._persist()
        self._store.append_event(
            {"event": "catalog_mounted", "catalog_id": cid, "name": info["name"]}
        )
        return record

    def mark_extension(self, catalog_id: str, note: str) -> Dict[str, Any]:
        if catalog_id not in self._catalogs:
            raise CatalogError("NOT_FOUND", f"类目不存在: {catalog_id}")
        self._catalogs[catalog_id]["extension_note"] = note
        self._persist()
        return self._catalogs[catalog_id]

    def get(self, catalog_id: str) -> Optional[Dict[str, Any]]:
        return self._catalogs.get(catalog_id)

    def require_implemented(self, catalog_id: str) -> Dict[str, Any]:
        cat = self._catalogs.get(catalog_id)
        if not cat:
            raise CatalogError("NOT_FOUND", f"类目不存在: {catalog_id}")
        if cat["implementation_status"] == "reserved":
            raise CatalogError(
                "RESERVED",
                "本阶段仅预留接口，未实现",
            )
        return cat

    def tree(self) -> Dict[str, Any]:
        roots: List[Dict[str, Any]] = []

        def build(cid: str) -> Dict[str, Any]:
            cat = self._catalogs[cid]
            node = {
                "catalog_id": cid,
                "name": cat["name"],
                "implementation_status": cat["implementation_status"],
                "env_requirements": cat["env_requirements"],
            }
            if cat.get("extension_note"):
                node["extension_note"] = cat["extension_note"]
            children = [
                build(k)
                for k, v in self._catalogs.items()
                if v["parent_id"] == cid
            ]
            if children:
                node["children"] = children
            return node

        for cid, cat in self._catalogs.items():
            if cat["parent_id"] == "ROOT":
                roots.append(build(cid))
        return {"catalogs": roots}

    def all(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._catalogs)