"""Adapter contract tests (design.md 3.1: T1/T2/T3/T5/T8/T10/T11)."""

from __future__ import annotations

import pytest

from adapter import boundary, pairing, portaudit, proxycheck, storage, whitelist
from adapter.errors import AdapterException, ErrorCode
from adapter.models import (
    CheckContext,
    DrillAction,
    RoundState,
    TriggerKind,
)
from adapter.receipt import DrillEngine


@pytest.fixture()
def evidence_dir(tmp_path):
    """Isolated evidence directory so tests never touch real audit streams."""
    return tmp_path / "audit"


@pytest.fixture()
def isolated_deny_log(tmp_path, monkeypatch):
    """Redirect the deny log into the test tmp dir."""
    path = tmp_path / "deny_log.jsonl"
    monkeypatch.setattr(whitelist, "DENY_LOG", path)
    return path


# ---------------------------------------------------------------- T1 (IF-3)
class TestWhitelist:
    def test_loopback_passes_w1(self, isolated_deny_log):
        result = whitelist.whitelist_validate("127.0.0.1", CheckContext.DISPATCH)
        assert result.passed is True
        assert result.matched_rule == "W1_loopback_v4"

    def test_kali_nat_passes_w3(self, isolated_deny_log):
        result = whitelist.whitelist_validate("192.168.25.128", CheckContext.DISPATCH)
        assert result.passed is True
        assert result.matched_rule == "W3_kali_nat_segment"

    def test_public_ip_denied(self, isolated_deny_log):
        result = whitelist.whitelist_validate("8.8.8.8", CheckContext.DISPATCH)
        assert result.passed is False
        assert result.deny_log_id is not None

    def test_hostname_denied_without_dns(self, isolated_deny_log):
        result = whitelist.whitelist_validate("evil.example.com", CheckContext.DISPATCH)
        assert result.passed is False

    def test_deny_log_written(self, isolated_deny_log):
        whitelist.whitelist_validate("8.8.8.8", CheckContext.DISPATCH)
        entries = whitelist.read_deny_log(isolated_deny_log)
        assert len(entries) == 1
        assert entries[0]["outbound_action"] == "blocked_before_emit"

    def test_config_missing_blocks(self, tmp_path, monkeypatch):
        monkeypatch.setattr(whitelist, "WHITELIST_CONFIG", tmp_path / "missing.json")
        with pytest.raises(AdapterException) as exc:
            whitelist.assert_loadable()
        assert exc.value.code == ErrorCode.E_WL_CONFIG_MISSING


# ------------------------------------------------------- T2/T5 (IF-1/IF-2)
class TestReceiptProtocol:
    def _ready_engine(self, evidence_dir) -> DrillEngine:
        engine = DrillEngine(evidence_dir=evidence_dir)
        engine.start_round(1)
        return engine

    def test_dispatch_accept_and_receipt_success(self, evidence_dir, isolated_deny_log):
        engine = self._ready_engine(evidence_dir)
        handle = engine.dispatch_task(
            1, 1, "127.0.0.1", DrillAction.TRAFFIC_DISGUISE, "scope note", TriggerKind.USER_COMMAND
        )
        assert handle.accepted is True
        ack = engine.report_receipt(handle.handle_id, "success", "evidence://trace-001")
        assert ack.state_next == RoundState.VERDICT_PENDING

    def test_dispatch_denies_whitelist_target(self, evidence_dir, isolated_deny_log):
        engine = self._ready_engine(evidence_dir)
        with pytest.raises(AdapterException) as exc:
            engine.dispatch_task(
                1, 1, "8.8.8.8", DrillAction.PROBE_SCAN, "note", TriggerKind.USER_COMMAND
            )
        assert exc.value.code == ErrorCode.E_TARGET_DENIED
        assert exc.value.detail["deny_log_id"]

    def test_dispatch_denies_unready_framework(self, evidence_dir, isolated_deny_log):
        engine = self._ready_engine(evidence_dir)
        with pytest.raises(AdapterException) as exc:
            engine.dispatch_task(
                1, 1, "127.0.0.1", DrillAction.PROBE_SCAN, "note", TriggerKind.USER_COMMAND
            )
        assert exc.value.code == ErrorCode.E_FRAMEWORK_OFFLINE

    def test_empty_conclusion_rejected(self, evidence_dir, isolated_deny_log):
        engine = self._ready_engine(evidence_dir)
        handle = engine.dispatch_task(
            1, 1, "127.0.0.1", DrillAction.TRAFFIC_DISGUISE, "note", TriggerKind.USER_COMMAND
        )
        with pytest.raises(AdapterException) as exc:
            engine.report_receipt(handle.handle_id, "", None)
        assert exc.value.code == ErrorCode.E_EMPTY_CONCLUSION

    def test_unknown_handle_rejected(self, evidence_dir):
        engine = DrillEngine(evidence_dir=evidence_dir)
        with pytest.raises(AdapterException) as exc:
            engine.report_receipt("no-such-handle", "success", None)
        assert exc.value.code == ErrorCode.E_HANDLE_UNKNOWN

    def test_trigger_must_be_enum(self, evidence_dir, isolated_deny_log):
        engine = self._ready_engine(evidence_dir)
        with pytest.raises(AdapterException) as exc:
            engine.dispatch_task(
                1, 1, "127.0.0.1", DrillAction.TRAFFIC_DISGUISE, "note", "poll_timer"
            )
        assert exc.value.code == ErrorCode.E_TRIGGER_ILLEGAL

    def test_round_must_exist(self, evidence_dir):
        engine = DrillEngine(evidence_dir=evidence_dir)
        with pytest.raises(AdapterException):
            engine.dispatch_task(
                9, 1, "127.0.0.1", DrillAction.TRAFFIC_DISGUISE, "note", TriggerKind.USER_COMMAND
            )


# ------------------------------------------------------------- T3 (IF-5)
class TestPortAudit:
    def test_addr_compliance_matrix(self):
        assert portaudit._addr_compliant("127.0.0.1") is True
        assert portaudit._addr_compliant("192.168.16.5") is True
        assert portaudit._addr_compliant("0.0.0.0") is False
        assert portaudit._addr_compliant("::") is False
        assert portaudit._addr_compliant("8.8.8.8") is False


# ------------------------------------------------------------- T8 (IF-4)
class TestBoundary:
    def test_stop_then_dispatch_refused(self, evidence_dir, isolated_deny_log):
        result = boundary.stop_on_boundary(
            {"source_step": 1, "target": "8.8.8.8", "captured_at": "now"}
        )
        assert result.stopped is True
        assert result.state == RoundState.AWAITING_USER
        assert boundary.is_blocked() is True

        engine = DrillEngine(evidence_dir=evidence_dir)
        engine.start_round(1)
        with pytest.raises(AdapterException) as exc:
            engine.dispatch_task(
                1, 1, "127.0.0.1", DrillAction.TRAFFIC_DISGUISE, "note", TriggerKind.USER_COMMAND
            )
        assert exc.value.code == ErrorCode.E_TARGET_DENIED

        boundary.reset_block()
        assert boundary.is_blocked() is False

    def test_established_connection_escalates(self):
        with pytest.raises(AdapterException) as exc:
            boundary.stop_on_boundary(
                {"source_step": 2, "target": "8.8.8.8", "captured_at": "now"},
                already_established=True,
            )
        assert exc.value.code == ErrorCode.E_BLOCK_FAILED
        boundary.reset_block()


# ------------------------------------------------------------ T10 (IF-10)
class TestPairing:
    def _dispatch(self, evidence_dir, isolated_deny_log):
        engine = DrillEngine(evidence_dir=evidence_dir)
        engine.start_round(2)
        return engine.dispatch_task(
            2, 1, "127.0.0.1", DrillAction.TRAFFIC_DISGUISE, "note", TriggerKind.RECEIPT_EVENT
        )

    def test_pair_complete(self, evidence_dir, isolated_deny_log):
        handle = self._dispatch(evidence_dir, isolated_deny_log)
        engine = DrillEngine(evidence_dir=evidence_dir)
        engine._steps[handle.handle_id] = engine._steps.get(handle.handle_id) or None  # placeholder
        # Re-dispatch on a shared engine view is unnecessary; write receipt stream.
        storage.append_record(
            "receipts",
            {
                "handle_id": handle.handle_id,
                "step_no": 1,
                "conclusion": "success",
                "evidence_ref": "capture://round-02.pcapng",
                "fact": "traffic disguised via ARTEX",
                "hint": "detection: TLS handshake only, no bare TCP",
            },
            base_dir=evidence_dir,
        )
        result = pairing.pairing_check(1, evidence_dir=evidence_dir)
        assert result["paired"] is True
        assert result["feature_pair_present"] is True

    def test_pair_missing_refs(self, evidence_dir, isolated_deny_log):
        handle = self._dispatch(evidence_dir, isolated_deny_log)
        storage.append_record(
            "receipts",
            {"handle_id": handle.handle_id, "step_no": 1, "conclusion": "success"},
            base_dir=evidence_dir,
        )
        with pytest.raises(AdapterException) as exc:
            pairing.pairing_check(1, evidence_dir=evidence_dir)
        assert exc.value.code == ErrorCode.E_PAIR_MISSING

    def test_pair_absent_defense(self, evidence_dir, isolated_deny_log):
        handle = self._dispatch(evidence_dir, isolated_deny_log)
        storage.append_record(
            "receipts",
            {
                "handle_id": handle.handle_id,
                "step_no": 1,
                "conclusion": "success",
                "evidence_ref": "capture://x.pcapng",
                "fact": "fact only",
            },
            base_dir=evidence_dir,
        )
        with pytest.raises(AdapterException) as exc:
            pairing.pairing_check(1, evidence_dir=evidence_dir)
        assert exc.value.code == ErrorCode.E_DEFENSE_PAIR_ABSENT


# ------------------------------------------------------------ T11 (IF-6)
class TestProxyCheck:
    def test_no_proxy_alive_passes(self, evidence_dir):
        result = proxycheck.proxy_alive_check(evidence_dir=evidence_dir)
        assert result.sidecar_alive is False
        assert result.tor_alive is False


# -------------------------------------------------------------- IF-9 core
class TestVerdict:
    def test_hidden_success(self, evidence_dir):
        from adapter import verdict

        report = verdict.verdict_from_counts(
            1,
            {
                "j1_plaintext_hits": 0,
                "j2_public_ip_hits": 0,
                "j3_abnormal_outbound": 0,
                "j4_disguise_valid": True,
                "j5_log_clean_hits": 0,
                "capture_contiguous": True,
                "audit_available": True,
            },
            evidence_dir=evidence_dir,
        )
        assert report["conclusion"] == "hidden_success"

    def test_hidden_failure_lists_items(self, evidence_dir):
        from adapter import verdict

        report = verdict.verdict_from_counts(
            1,
            {
                "j1_plaintext_hits": 3,
                "j2_public_ip_hits": 0,
                "j3_abnormal_outbound": 1,
                "j4_disguise_valid": False,
                "j5_log_clean_hits": 0,
                "capture_contiguous": True,
                "audit_available": True,
            },
            evidence_dir=evidence_dir,
        )
        assert report["conclusion"] == "hidden_failure"
        assert "j1_plaintext_hits" in report["reason"]

    def test_evidence_insufficient(self, evidence_dir):
        from adapter import verdict

        report = verdict.verdict_from_counts(
            1,
            {
                "j1_plaintext_hits": 0,
                "j2_public_ip_hits": 0,
                "j3_abnormal_outbound": 0,
                "j4_disguise_valid": True,
                "j5_log_clean_hits": 0,
                "capture_contiguous": False,
                "audit_available": True,
            },
            evidence_dir=evidence_dir,
        )
        assert report["conclusion"] == "evidence_insufficient"

    def test_missing_counts_raise(self, evidence_dir):
        from adapter import verdict

        with pytest.raises(AdapterException) as exc:
            verdict.verdict_from_counts(1, {"j1_plaintext_hits": 0}, evidence_dir=evidence_dir)
        assert exc.value.code == ErrorCode.E_EVIDENCE_MISSING
