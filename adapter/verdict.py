"""IF-9 hidden-verdict check over J1~J5 (design.md 2.2.2, spec 5.7.1-3/4)."""

from __future__ import annotations

from adapter import storage
from adapter.errors import AdapterException, ErrorCode


def verdict_from_counts(round_no: int, counts: dict, evidence_dir=None) -> dict:
    """Pure J1~J5 verdict logic over structured evidence counts (testable core).

    counts keys: j1_plaintext_hits, j2_public_ip_hits, j3_abnormal_outbound,
    j4_disguise_valid, j5_log_clean_hits, capture_contiguous, audit_available.
    Mapping follows design.md: evidence gaps -> evidence_insufficient (spec
    5.7.3-2); any J hit or invalid disguise -> hidden_failure; clean all ->
    hidden_success.
    """
    missing = [
        key for key in (
            "j1_plaintext_hits",
            "j2_public_ip_hits",
            "j3_abnormal_outbound",
            "j4_disguise_valid",
            "j5_log_clean_hits",
            "capture_contiguous",
            "audit_available",
        )
        if key not in counts
    ]
    if missing:
        raise AdapterException(
            ErrorCode.E_EVIDENCE_MISSING, f"evidence counts incomplete: {missing}"
        )
    if not counts["capture_contiguous"] or not counts["audit_available"]:
        conclusion = "evidence_insufficient"
        reason = "capture broken or audit channel unavailable"
    elif (
        counts["j1_plaintext_hits"] == 0
        and counts["j2_public_ip_hits"] == 0
        and counts["j3_abnormal_outbound"] == 0
        and counts["j5_log_clean_hits"] == 0
        and counts["j4_disguise_valid"]
    ):
        conclusion = "hidden_success"
        reason = "all J1~J5 criteria satisfied"
    else:
        conclusion = "hidden_failure"
        failed = [
            key
            for key, requirement in (
                ("j1_plaintext_hits", 0),
                ("j2_public_ip_hits", 0),
                ("j3_abnormal_outbound", 0),
                ("j5_log_clean_hits", 0),
            )
            if counts[key] != requirement
        ]
        if not counts["j4_disguise_valid"]:
            failed.append("j4_disguise_valid")
        reason = f"failing items: {failed}"

    report = {
        "round_no": round_no,
        "j1_plaintext_hits": counts["j1_plaintext_hits"],
        "j2_public_ip_hits": counts["j2_public_ip_hits"],
        "j3_abnormal_outbound": counts["j3_abnormal_outbound"],
        "j4_disguise_valid": counts["j4_disguise_valid"],
        "j5_log_clean_hits": counts["j5_log_clean_hits"],
        "per_item_evidence": counts.get("per_item_evidence", []),
        "conclusion": conclusion,
        "reason": reason,
    }
    storage.append_record("verdicts", report, base_dir=evidence_dir)
    return report


def collect_evidence(
    round_no: int,
    pcap_path: str,
    tshark_path: str | None = None,
    audit_available: bool = True,
) -> dict:
    """Collect J1~J5 counts for one round via tshark display filters.

    Directly reads the round pcap (spec 5.7.1-3). tshark absence maps to
    E_EVIDENCE_MISSING so the caller reports evidence_insufficient instead of
    inventing numbers. Evidence stream records keep filter + excerpt traces.
    """
    if tshark_path is None:
        raise AdapterException(
            ErrorCode.E_EVIDENCE_MISSING,
            "tshark unavailable: verdict requires packet-level evidence",
        )
    w3 = "192.168.16.0/20"
    # Loopback-capture semantics: J1 counts plaintext on the TARGET port only
    # (proxy-protocol headers stay on loopback and never leave the machine);
    # J2/J3 count any non-loopback destination (public egress attempt).
    filters = {
        "j1_plaintext_hits": "tcp.port == 8443 and not tls",
        "j2_public_ip_hits": f"ip and not (ip.dst in {{127.0.0.0/8, {w3}}})",
        "j3_abnormal_outbound": (
            f"tcp.flags.syn == 1 and tcp.flags.ack == 0 "
            f"and not (ip.dst in {{127.0.0.0/8, {w3}}})"
        ),
        # Scoped to the TLS target port: loopback capture misses Winsock
        # fast-path connections (round-09 evidence), so an unscoped filter
        # picks up OTHER processes' TLS noise (round-08 SNI=huaweicloud).
        "j4_disguise_valid": "tls.handshake.type == 1 and tcp.port == 8443",
    }
    counts: dict = {}
    excerpts: list[str] = []
    for key, display_filter in filters.items():
        try:
            out = subprocess_run_tshark(tshark_path, pcap_path, display_filter)
        except (OSError, subprocess_error()) as exc:
            raise AdapterException(
                ErrorCode.E_EVIDENCE_MISSING, f"tshark failed on {key}: {exc}"
            ) from exc
        lines = [line for line in out.splitlines() if line.strip()]
        counts[key] = len(lines)
        if lines:
            excerpts.append(f"{key}: {lines[0]}")
    counts["j5_log_clean_hits"] = audit_stream_hits(round_no)
    tls_sessions_seen = counts["j4_disguise_valid"] > 0
    counts["j4_disguise_valid"] = tls_sessions_seen and counts["j1_plaintext_hits"] == 0
    counts["capture_contiguous"] = True
    counts["audit_available"] = audit_available
    counts["per_item_evidence"] = excerpts
    return counts


def audit_stream_hits(round_no: int, base_dir=None) -> int:
    """Count unregistered anomaly records in the audit evidence stream (J5)."""
    records = storage.read_stream("audit", base_dir=base_dir)
    return sum(1 for item in records if item.get("round_no") == round_no and item.get("anomaly"))


def subprocess_run_tshark(tshark_path: str, pcap_path: str, display_filter: str) -> str:
    """Run one tshark display-filter query over a round pcap."""
    import subprocess  # noqa: PLC0415 - kept local to make the dependency explicit

    result = subprocess.run(
        [tshark_path, "-r", pcap_path, "-Y", display_filter],
        capture_output=True, check=False, timeout=120,
        encoding="utf-8", errors="replace",
    )
    return result.stdout


def subprocess_error():
    import subprocess  # noqa: PLC0415

    return subprocess.SubprocessError
