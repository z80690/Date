"""IF-4 stop-on-boundary blocker (design.md 2.2.2, spec 4.3.2-2)."""

from __future__ import annotations

from adapter import storage
from adapter.errors import AdapterException, ErrorCode
from adapter.models import RoundState, StopResult

# Module-level kill switch: once tripped, dispatch_task must refuse everything.
_BLOCKED = False


def is_blocked() -> bool:
    """True after any boundary event until the user explicitly releases."""
    return _BLOCKED


def reset_block() -> None:
    """Release the block ONLY on explicit user ruling (spec 4.3.2-2)."""
    global _BLOCKED
    _BLOCKED = False


def stop_on_boundary(boundary_event: dict, already_established: bool = False) -> StopResult:
    """Trip the global outbound block on a boundary event (IF-4 contract).

    The event carries source_step / target / captured_at. The adapter halts
    the action bookkeeping, blocks all further outbound dispatch, and moves
    to awaiting_user. A connection that was already established cannot be
    torn down by the adapter itself -> E_BLOCK_FAILED escalation (design.md).
    """
    global _BLOCKED
    record_id = storage.append_record(
        "boundary",
        {
            **boundary_event,
            "outbound_blocked": not already_established,
            "escalated": already_established,
        },
    )
    _BLOCKED = True
    if already_established:
        raise AdapterException(
            ErrorCode.E_BLOCK_FAILED,
            "connection already established; escalate to user with full event trail",
            detail={"record_id": record_id, "event": boundary_event},
        )
    return StopResult(stopped=True, outbound_blocked=True, state=RoundState.AWAITING_USER)
