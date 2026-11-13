"""P003 drill adapter error codes (design.md 2.2.2 exception mappings)."""

from __future__ import annotations

from enum import StrEnum


class ErrorCode(StrEnum):
    """Contract error codes, verbatim from design.md 2.2.2 exception mappings."""

    E_TARGET_DENIED = "E_TARGET_DENIED"
    E_ACTION_UNSUPPORTED = "E_ACTION_UNSUPPORTED"
    E_FRAMEWORK_OFFLINE = "E_FRAMEWORK_OFFLINE"
    E_TRIGGER_ILLEGAL = "E_TRIGGER_ILLEGAL"
    E_EMPTY_CONCLUSION = "E_EMPTY_CONCLUSION"
    E_HANDLE_UNKNOWN = "E_HANDLE_UNKNOWN"
    E_WL_CONFIG_MISSING = "E_WL_CONFIG_MISSING"
    E_BLOCK_FAILED = "E_BLOCK_FAILED"
    E_BIND_NON_LOOPBACK = "E_BIND_NON_LOOPBACK"
    E_AUDIT_TOOL_MISSING = "E_AUDIT_TOOL_MISSING"
    E_PROXY_STOP_FAILED = "E_PROXY_STOP_FAILED"
    E_KB_NOT_REGISTERED = "E_KB_NOT_REGISTERED"
    E_CAPTURE_BROKEN = "E_CAPTURE_BROKEN"
    E_IFACE_UNAVAILABLE = "E_IFACE_UNAVAILABLE"
    E_EVIDENCE_MISSING = "E_EVIDENCE_MISSING"
    E_AUDIT_CHANNEL_BROKEN = "E_AUDIT_CHANNEL_BROKEN"
    E_PAIR_MISSING = "E_PAIR_MISSING"
    E_DEFENSE_PAIR_ABSENT = "E_DEFENSE_PAIR_ABSENT"
    E_REPORT_INCOMPLETE = "E_REPORT_INCOMPLETE"
    E_BASELINE_NOT_REPEATABLE = "E_BASELINE_NOT_REPEATABLE"


class AdapterException(Exception):
    """Contract exception carrying a design.md error code plus evidence detail."""

    def __init__(self, code: ErrorCode, message: str, detail: dict | None = None) -> None:
        self.code = code
        self.detail = detail or {}
        super().__init__(f"{code.value}: {message}")
