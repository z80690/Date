"""IF-8 capture session management over dumpcap (design.md 2.2.2, spec 5.7.1-1).

Sessions are event-driven: health_check runs when a receipt arrives (spec
6.2-3), never on a timer. A broken session invalidates the whole round.
"""

from __future__ import annotations

import signal
import subprocess
from pathlib import Path

from adapter import storage
from adapter.config import round_dir
from adapter.errors import AdapterException, ErrorCode
from adapter.models import CaptureResult, RoundState

DUMPCAP = Path(r"C:\Program Files\Wireshark\dumpcap.exe")

_SESSIONS: dict[str, dict] = {}


def _assert_tool() -> None:
    if not DUMPCAP.is_file():
        raise AdapterException(
            ErrorCode.E_AUDIT_TOOL_MISSING,
            f"dumpcap not found at {DUMPCAP}; finish Wireshark install first",
        )


def capture_session(
    op: str,
    iface: str,
    round_no: int,
    evidence_dir=None,
) -> CaptureResult:
    """Start/stop/health-check one per-round capture session (IF-8 contract)."""
    _assert_tool()
    if op == "start":
        return _start(iface, round_no, evidence_dir)
    if op == "stop":
        return _stop(round_no, evidence_dir)
    if op == "health_check":
        return _health(round_no, evidence_dir)
    raise AdapterException(ErrorCode.E_IFACE_UNAVAILABLE, f"unknown capture op: {op}")


def _start(iface: str, round_no: int, evidence_dir=None) -> CaptureResult:
    pcap = round_dir(round_no) / f"round-{round_no:02d}.pcapng"
    try:
        proc = subprocess.Popen(
            [str(DUMPCAP), "-i", iface, "-w", str(pcap)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    except OSError as exc:
        raise AdapterException(
            ErrorCode.E_IFACE_UNAVAILABLE, f"capture start failed on {iface}: {exc}"
        ) from exc
    session_id = storage.uuid_hex()
    started_at = storage.now_iso()
    _SESSIONS[session_id] = {
        "proc": proc,
        "pcap": pcap,
        "iface": iface,
        "round_no": round_no,
        "started_at": started_at,
    }
    storage.append_record(
        "captures",
        {
            "session_id": session_id,
            "op": "start",
            "iface": iface,
            "round_no": round_no,
            "pcap_path": str(pcap),
            "started_at": started_at,
        },
        base_dir=evidence_dir,
    )
    return CaptureResult(session_id=session_id, started_at=started_at, pcap_path=str(pcap))


def _stop(round_no: int, evidence_dir=None) -> CaptureResult:
    session_id, session = _find_by_round(round_no)
    if session is None:
        raise AdapterException(
            ErrorCode.E_CAPTURE_BROKEN, f"no capture session for round {round_no}"
        )
    # Graceful stop: TerminateProcess hard-kills dumpcap and loses its write
    # buffer; CTRL_BREAK lets it flush the pcapng to disk first.
    session["proc"].send_signal(signal.CTRL_BREAK_EVENT)
    try:
        session["proc"].wait(timeout=15)
    except subprocess.TimeoutExpired:
        session["proc"].terminate()
    result = CaptureResult(
        session_id=session_id,
        started_at=session["started_at"],
        pcap_path=str(session["pcap"]),
        contiguous=Path(session["pcap"]).is_file(),
    )
    storage.append_record(
        "captures",
        {
            "session_id": session_id,
            "op": "stop",
            "round_no": round_no,
            "pcap_path": result.pcap_path,
            "contiguous": result.contiguous,
        },
        base_dir=evidence_dir,
    )
    _SESSIONS.pop(session_id, None)
    if not result.contiguous:
        raise AdapterException(
            ErrorCode.E_CAPTURE_BROKEN,
            "round evidence invalid: pcap file missing at stop",
            detail={"session_id": session_id},
        )
    return result


def _health(round_no: int, evidence_dir=None) -> CaptureResult:
    """Receipt-attached liveness probe (no timer loop, spec 6.2-3)."""
    session_id, session = _find_by_round(round_no)
    alive = session is not None and session["proc"].poll() is None
    if not alive:
        raise AdapterException(
            ErrorCode.E_CAPTURE_BROKEN,
            f"capture session dead for round {round_no}: whole round must be re-run",
        )
    storage.append_record(
        "captures",
        {"session_id": session_id, "op": "health_check", "round_no": round_no, "alive": True},
        base_dir=evidence_dir,
    )
    return CaptureResult(session_id=session_id, contiguous=True)


def _find_by_round(round_no: int) -> tuple[str | None, dict | None]:
    for session_id, session in _SESSIONS.items():
        if session["round_no"] == round_no:
            return session_id, session
    return None, None


def assert_round_capturable(round_no: int) -> None:
    """Gate used by the drill flow: round must not be in a failed verdict state."""
    from adapter.receipt import DrillEngine  # noqa: PLC0415 - avoid import cycle at module load

    engine = DrillEngine()
    if engine.round_state(round_no) == RoundState.VERDICT_FAILURE:
        raise AdapterException(
            ErrorCode.E_CAPTURE_BROKEN,
            f"round {round_no} failed verdict; fixes required before re-run",
        )
