"""IF-1/IF-2 receipt-protocol core: dispatch, receipt, round state machine.

The receipt is the sole driver of state transitions (spec 4.2-1); dispatch is
the sole outbound path and every target must pass IF-3 before anything else
happens (spec 4.3.2-1). All bookkeeping lands in JSONL evidence streams.
"""

from __future__ import annotations

from adapter import storage
from adapter.boundary import is_blocked
from adapter.errors import AdapterException, ErrorCode
from adapter.models import (
    DrillAction,
    ReceiptAck,
    RoundState,
    StepRecord,
    StepState,
    TaskHandle,
    TriggerKind,
)
from adapter.whitelist import whitelist_validate

# Framework readiness mirrors gates/deploy-selfcheck.md (single source of truth
# updated after each deployment change; PentAGI pending mirror recovery).
FRAMEWORK_READY: dict[str, bool] = {"artex": True, "cairn": True, "pentagi": False}

# Action -> owning framework (design.md 2.2.2 IF-1 business note).
ACTION_FRAMEWORK = {
    DrillAction.PROBE_SCAN: "pentagi",
    DrillAction.MSF_LOCAL_MODULE: "pentagi",
    DrillAction.TRAFFIC_DISGUISE: "artex",
    DrillAction.HEARTBEAT_SIM: "artex",
}


class DrillEngine:
    """Round/step state machine backing IF-1 dispatch and IF-2 receipt."""

    def __init__(self, evidence_dir=None) -> None:
        self.evidence_dir = evidence_dir
        self._rounds: dict[int, RoundState] = {}
        self._steps: dict[str, StepRecord] = {}
        self._plans: dict[int, int | None] = {}

    # -- IF-1 ---------------------------------------------------------------
    def dispatch_task(
        self,
        round_no: int,
        step_no: int,
        target: str,
        action: DrillAction,
        tool_scope_note: str,
        trigger: TriggerKind,
    ) -> TaskHandle:
        """Validate and accept one atomic drill step (IF-1 contract)."""
        if not isinstance(trigger, TriggerKind):
            raise AdapterException(
                ErrorCode.E_TRIGGER_ILLEGAL,
                "trigger must be user_command or receipt_event",
            )
        if not isinstance(action, DrillAction):
            raise AdapterException(
                ErrorCode.E_ACTION_UNSUPPORTED, f"unknown action: {action}"
            )
        state = self._rounds.get(round_no)
        if state != RoundState.RUNNING:
            raise AdapterException(
                ErrorCode.E_FRAMEWORK_OFFLINE,
                f"round {round_no} is {state}; dispatch requires running state",
            )
        if is_blocked():
            raise AdapterException(
                ErrorCode.E_TARGET_DENIED,
                "adapter is in stop-on-boundary state; awaiting user ruling",
            )
        check = whitelist_validate(target, "dispatch")
        if not check.passed:
            raise AdapterException(
                ErrorCode.E_TARGET_DENIED,
                f"target {target} outside whitelist",
                detail={"deny_log_id": check.deny_log_id, "context": "dispatch"},
            )
        framework = ACTION_FRAMEWORK[action]
        if not FRAMEWORK_READY.get(framework, False):
            raise AdapterException(
                ErrorCode.E_FRAMEWORK_OFFLINE,
                f"framework {framework} not ready for action {action.value}",
            )

        handle = TaskHandle(
            handle_id=storage.uuid_hex(),
            accepted=True,
            round_no=round_no,
            step_no=step_no,
            target=target,
            action=action,
        )
        record = StepRecord(
            round_no=round_no,
            step_no=step_no,
            handle_id=handle.handle_id,
            target=target,
            action=action,
            trigger=trigger,
            state=StepState.RUNNING,
            started_at=storage.now_iso(),
            evidence_ref=tool_scope_note,
        )
        self._steps[handle.handle_id] = record
        storage.append_record(
            "dispatches",
            {
                "handle_id": handle.handle_id,
                "round_no": round_no,
                "step_no": step_no,
                "target": target,
                "action": action.value,
                "trigger": trigger.value,
                "matched_rule": check.matched_rule,
                "framework": framework,
                "tool_scope_note": tool_scope_note,
            },
            base_dir=self.evidence_dir,
        )
        return handle

    # -- IF-2 ---------------------------------------------------------------
    def report_receipt(
        self,
        handle_id: str,
        conclusion: str,
        evidence_ref: str | None,
        hint: str | None = None,
        fact: str | None = None,
    ) -> ReceiptAck:
        """Accept an execution receipt and drive the state machine (IF-2)."""
        if not conclusion:
            raise AdapterException(
                ErrorCode.E_EMPTY_CONCLUSION, "receipt conclusion must not be empty"
            )
        record = self._steps.get(handle_id)
        if record is None or record.state != StepState.RUNNING:
            raise AdapterException(
                ErrorCode.E_HANDLE_UNKNOWN, f"handle unknown or not running: {handle_id}"
            )
        record.state = StepState.DONE if conclusion == "success" else StepState.FAILED
        record.receipt_at = storage.now_iso()
        record.conclusion = conclusion
        record.evidence_ref = evidence_ref
        if fact:
            # Fact registration lands in the local evidence stream; Cairn MCP
            # registration is performed agent-side against this reference.
            record.tags.append(f"fact_registered:{fact[:80]}")

        storage.append_record(
            "receipts",
            {
                "handle_id": handle_id,
                "round_no": record.round_no,
                "step_no": record.step_no,
                "conclusion": conclusion,
                "evidence_ref": evidence_ref,
                "hint": hint,
                "fact": fact,
            },
            base_dir=self.evidence_dir,
        )

        state_next = self._round_state_after(record.round_no)
        self._rounds[record.round_no] = state_next
        ack = ReceiptAck(ack_id=storage.uuid_hex(), state_next=state_next)
        storage.append_record(
            "rounds",
            {"round_no": record.round_no, "state_next": state_next.value, "ack_id": ack.ack_id},
            base_dir=self.evidence_dir,
        )
        return ack

    def _round_state_after(self, round_no: int) -> RoundState:
        steps = [s for s in self._steps.values() if s.round_no == round_no]
        if any(s.state == StepState.FAILED for s in steps):
            return RoundState.ROUND_FAILED
        plan = self._plans.get(round_no)
        if (
            steps
            and all(s.state == StepState.DONE for s in steps)
            and (plan is None or len(steps) >= plan)
        ):
            return RoundState.VERDICT_PENDING
        # Plan not yet fulfilled (or undeclared): keep running for next dispatch.
        return RoundState.RUNNING

    # -- round lifecycle ----------------------------------------------------
    def start_round(self, round_no: int, total_steps: int | None = None) -> RoundState:
        """Open a round in running state, declaring its planned step count.

        A declared plan gates verdict_pending: the round only moves to
        verdict_pending once every planned step has a successful receipt.
        Undeclared (None) keeps the legacy single-step behavior.
        """
        if round_no in self._rounds:
            raise AdapterException(
                ErrorCode.E_HANDLE_UNKNOWN, f"round {round_no} already exists"
            )
        self._rounds[round_no] = RoundState.RUNNING
        self._plans[round_no] = total_steps
        storage.append_record(
            "rounds",
            {
                "round_no": round_no,
                "state_next": RoundState.RUNNING.value,
                "total_steps": total_steps,
            },
            base_dir=self.evidence_dir,
        )
        return RoundState.RUNNING

    def round_state(self, round_no: int) -> RoundState:
        """Current round state (running steps stay running until receipts)."""
        state = self._rounds.get(round_no)
        if state is None:
            raise AdapterException(ErrorCode.E_HANDLE_UNKNOWN, f"round unknown: {round_no}")
        if state == RoundState.RUNNING:
            running = any(
                s.state == StepState.RUNNING for s in self._steps.values() if s.round_no == round_no
            )
            return RoundState.RUNNING if running else state
        return state
