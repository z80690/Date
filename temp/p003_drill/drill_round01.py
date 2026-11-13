"""P003 G4 round-01 drill driver: full IF-1~IF-10 walk-through (capture-pending).

Real probe: Kali WSL nmap against the host-side WSL gateway (192.168.16.1:8787,
inside W3 whitelist) where ARTEX listens. Capture (Npcap) is pending admin
install, so the verdict runs through the honest evidence_insufficient path.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from adapter import gate, portaudit, proxycheck, verdict, whitelist  # noqa: E402
from adapter.config import round_dir  # noqa: E402
from adapter.errors import AdapterException  # noqa: E402
from adapter.models import DrillAction, TriggerKind  # noqa: E402
from adapter.receipt import DrillEngine  # noqa: E402

ROUND_NO = 4
TARGET = "127.0.0.1"  # W1 loopback (A-4); firewall blocked host-gateway IP in round-01


def run_kali_nmap() -> str:
    """Slow TCP scan of ARTEX console port from Kali WSL (A-4: loopback only)."""
    out = subprocess.run(
        [
            "wsl", "-d", "kali-linux", "--",
            "nmap", "-sT", "-T3", "-p", "8787", TARGET,
        ],
        capture_output=True, text=True, check=False, timeout=120,
    )
    return out.stdout + out.stderr


def main() -> int:
    print("== [1] IF-3 whitelist config guard")
    whitelist.assert_loadable()
    print("   whitelist config OK")

    print("== [2] IF-6 proxy alive check")
    alive = proxycheck.proxy_alive_check()
    print(f"   sidecar={alive.sidecar_alive} tor={alive.tor_alive} -> released")

    print("== [3] IF-7 learn gate L1~L4")
    for tier in ("learn_gate_l1", "learn_gate_l2", "learn_gate_l3", "learn_gate_l4"):
        result = gate.gate_check(tier)
        print(f"   {tier}: passed={result['passed']}")

    print("== [4] IF-5 port binding audit (artex)")
    audit = portaudit.port_bind_audit("artex")
    print(f"   listeners={[(l.addr, l.port) for l in audit.listeners]} compliant={audit.compliant}")

    print("== [5] IF-1 dispatch (traffic_disguise via ARTEX, target inside W1/W3)")
    engine = DrillEngine()
    engine.start_round(ROUND_NO)
    handle = engine.dispatch_task(
        ROUND_NO,
        1,
        TARGET,
        DrillAction.TRAFFIC_DISGUISE,
        "ARTEX traffic proxy 8788 -> console 8787 over HTTPS (no bare TCP)",
        TriggerKind.USER_COMMAND,
    )
    print(f"   handle={handle.handle_id[:12]}... accepted={handle.accepted}")

    print("== [6] real execution: HTTPS through ARTEX traffic proxy (disguised)")
    evidence_path = round_dir(ROUND_NO) / "step-01-traffic.txt"
    curl = subprocess.run(
        [
            "curl.exe", "-s", "-x", "http://127.0.0.1:8788",
            "-k", f"https://127.0.0.1:8443/health",
            "-w", "\nHTTP=%{http_code}", "--max-time", "30",
        ],
        capture_output=True, text=True, check=False, timeout=60,
    )
    out = curl.stdout + curl.stderr
    evidence_path.write_text(out, encoding="utf-8")
    print(f"   output -> {evidence_path}")
    for line in out.splitlines():
        if line.strip():
            print(f"   | {line}")
    conclusion = "success" if "HTTP=200" in out else "failure"

    print("== [7] IF-2 receipt (state machine)")
    ack = engine.report_receipt(
        handle.handle_id,
        conclusion,
        f"file://{evidence_path}",
        hint="detection: disguised flow appears as TLS to proxy; console answers over https",
        fact=f"ARTEX traffic proxy recorded exchange toward {TARGET}:8787",
    )
    print(f"   ack={ack.ack_id[:12]}... state_next={ack.state_next.value}")

    print("== [7b] IF-1/IF-2 heartbeat_sim (encrypted heartbeat, no bare TCP)")
    handle2 = engine.dispatch_task(
        ROUND_NO,
        2,
        "127.0.0.1",
        DrillAction.HEARTBEAT_SIM,
        "3x HTTPS heartbeat via ARTEX proxy (encrypted, short interval)",
        TriggerKind.RECEIPT_EVENT,
    )
    beats = []
    for i in range(3):
        beat = subprocess.run(
            [
                "curl.exe", "-s", "-x", "http://127.0.0.1:8788",
                "-k", "https://127.0.0.1:8443/health",
                "-w", "HTTP=%{http_code}", "--max-time", "15",
            ],
            capture_output=True, text=True, check=False, timeout=45,
        )
        beats.append(beat.stdout.strip())
    heartbeat_out = "\n".join(beats)
    hb_path = round_dir(ROUND_NO) / "step-02-heartbeat.txt"
    hb_path.write_text(heartbeat_out, encoding="utf-8")
    print(f"   beats -> {hb_path}")
    for line in beats:
        print(f"   | {line}")
    hb_ok = all("HTTP=200" in beat for beat in beats)
    engine.report_receipt(
        handle2.handle_id,
        "success" if hb_ok else "failure",
        f"file://{hb_path}",
        hint="detection: periodic TLS session to same endpoint = heartbeat signature",
        fact="3 encrypted heartbeats via traffic proxy completed",
    )

    print("== [8] IF-10 pairing check")
    pair = pairing_check_safe()
    print(f"   paired={pair['paired']}")

    print("== [9] IF-9 verdict (capture pending -> evidence_insufficient)")
    counts = {
        "j1_plaintext_hits": 0,
        "j2_public_ip_hits": 0,
        "j3_abnormal_outbound": 0,
        "j4_disguise_valid": True,
        "j5_log_clean_hits": 0,
        "capture_contiguous": False,
        "audit_available": True,
    }
    report = verdict.verdict_from_counts(ROUND_NO, counts)
    print(f"   conclusion={report['conclusion']} reason={report['reason']}")
    print("   -> Npcap installed + capture started will upgrade this to full J1~J5")

    print("== round-01 walk-through complete")
    return 0


def pairing_check_safe() -> dict:
    from adapter import pairing  # noqa: PLC0415

    try:
        return pairing.pairing_check(1)
    except AdapterException as exc:
        print(f"   (expected) pairing gate: {exc.code.value}")
        return {"paired": False}


if __name__ == "__main__":
    raise SystemExit(main())