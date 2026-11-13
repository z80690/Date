"""Core data model for the P003 drill adapter (design.md 2.2.1, contract v1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

CONTRACT_VERSION = "v1"


class DrillAction(StrEnum):
    """Atomic single-step actions (IF-1 action enum)."""

    PROBE_SCAN = "probe_scan"
    MSF_LOCAL_MODULE = "msf_local_module"
    TRAFFIC_DISGUISE = "traffic_disguise"
    HEARTBEAT_SIM = "heartbeat_sim"


class TriggerKind(StrEnum):
    """Event-driven trigger sources, exactly two values (spec 6.2-3)."""

    USER_COMMAND = "user_command"
    RECEIPT_EVENT = "receipt_event"


class CheckContext(StrEnum):
    """IF-3 validation contexts for every network-bound action."""

    DISPATCH = "dispatch"
    DISGUISE = "disguise"
    HEARTBEAT = "heartbeat"
    DNS_CHECK = "dns_check"


class StepState(StrEnum):
    """Per-step state machine (spec 4.2-1: receipt is the sole state driver)."""

    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class RoundState(StrEnum):
    """Per-round state machine driven exclusively by receipts (spec 4.2-1)."""

    PENDING = "pending"
    RUNNING = "running"
    AWAITING_USER = "awaiting_user"
    ROUND_FAILED = "round_failed"
    VERDICT_PENDING = "verdict_pending"
    VERDICT_SUCCESS = "verdict_success"
    VERDICT_FAILURE = "verdict_failure"


@dataclass(frozen=True)
class TaskHandle:
    """IF-1 return payload."""

    handle_id: str
    accepted: bool
    round_no: int
    step_no: int
    target: str
    action: DrillAction


@dataclass(frozen=True)
class ReceiptAck:
    """IF-2 return payload."""

    ack_id: str
    state_next: RoundState


@dataclass(frozen=True)
class CheckResult:
    """IF-3 return payload."""

    passed: bool
    matched_rule: str | None = None
    deny_log_id: str | None = None


@dataclass(frozen=True)
class StopResult:
    """IF-4 return payload."""

    stopped: bool
    outbound_blocked: bool
    state: RoundState


@dataclass(frozen=True)
class Listener:
    """One TCP listening endpoint observed by IF-5."""

    addr: str
    port: int
    pid: int | None = None


@dataclass(frozen=True)
class BindAuditResult:
    """IF-5 return payload."""

    listeners: list[Listener]
    compliant: bool


@dataclass(frozen=True)
class AliveResult:
    """IF-6 return payload."""

    sidecar_alive: bool
    tor_alive: bool
    process_hint: str | None = None


@dataclass(frozen=True)
class CaptureResult:
    """IF-8 return payload."""

    session_id: str
    started_at: str | None = None
    pcap_path: str | None = None
    contiguous: bool | None = None


@dataclass
class StepRecord:
    """Persistent per-step record (evidence backbone for IF-9/IF-10)."""

    round_no: int
    step_no: int
    handle_id: str
    target: str
    action: DrillAction
    trigger: TriggerKind
    state: StepState
    started_at: str
    receipt_at: str | None = None
    conclusion: str | None = None
    evidence_ref: str | None = None
    capture_ref: str | None = None
    audit_ref: str | None = None
    feature_pair_present: bool = False
    tags: list[str] = field(default_factory=list)
