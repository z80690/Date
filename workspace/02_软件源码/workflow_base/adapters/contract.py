"""统一适配契约（任务 3.1）。

类目级适配契约 + 对象级适配契约（能力声明三要素），版本 v1。
契约符合性校验供类目注册中心挂载时调用（对接 2.2）。
"""

from __future__ import annotations

from typing import Any, Dict, List

CONTRACT_VERSION = "v1"

CATALOG_CONTRACT_FIELDS = (
    "catalog_id",
    "name",
    "parent_id",
    "implementation_status",
    "env_requirements",
    "adapter_kind",
    "receipt_semantics",
)
OBJECT_CONTRACT_FIELDS = (
    "object_id",
    "catalog_id",
    "capability",
    "status",
)
CAPABILITY_FIELDS = ("actions", "result_types")


class ContractError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def validate_catalog_contract(info: Dict[str, Any]) -> None:
    missing = [k for k in CATALOG_CONTRACT_FIELDS if k not in info]
    if missing:
        raise ContractError(
            "CONTRACT_INCOMPLETE",
            f"类目级契约字段缺失: {missing}（契约版本 {CONTRACT_VERSION}）",
        )
    if info.get("adapter_kind") != "catalog_adapter":
        raise ContractError(
            "CONTRACT_KIND_BAD",
            "adapter_kind 必须为 catalog_adapter（领域逻辑只能活在适配层，5.1.1 规则 4）",
        )
    if not str(info.get("receipt_semantics", "")).strip():
        raise ContractError("RECEIPT_SEMANTICS_MISSING", "回执语义说明缺失")


def validate_object_contract(obj: Dict[str, Any]) -> None:
    missing = [k for k in OBJECT_CONTRACT_FIELDS if k not in obj]
    if missing:
        raise ContractError(
            "OBJECT_CONTRACT_INCOMPLETE",
            f"对象级契约字段缺失: {missing}；注册被拒并返回缺失项（5.3.1 规则 4）",
        )
    cap = obj.get("capability") or {}
    cap_missing = [k for k in CAPABILITY_FIELDS if not cap.get(k)]
    if cap_missing:
        raise ContractError(
            "CAPABILITY_INCOMPLETE",
            f"能力声明三要素缺失: {cap_missing}（动作清单/参数范围/可上报结果类型，6.2.3）",
        )
    for a in cap["actions"]:
        if "name" not in a or "params_scope" not in a:
            raise ContractError(
                "ACTION_DECL_BAD",
                "每个动作须含 name 与 params_scope（参数范围）",
            )