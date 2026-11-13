"""P003 G4 round-06: full drill WITH capture -> IF-8 start/stop + IF-9 J1~J5.

Flow: IF-8 capture start (Npcap loopback) -> traffic_disguise + heartbeat_sim
(real HTTPS through ARTEX proxy) -> capture stop -> IF-9 collect_evidence via
tshark -> verdict_from_counts -> hidden_success / hidden_failure verdict.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from adapter import capture, pairing, portaudit, proxycheck, verdict, whitelist  # noqa: E402
from adapter.config import round_dir  # noqa: E402
from adapter.errors import AdapterException  # noqa: E402
from adapter.models import DrillAction, TriggerKind  # noqa: E402
from adapter.receipt import DrillEngine  # noqa: E402

ROUND_NO = 9
TARGET = "127.0.0.1"
TLS_URL = "https://127.0.0.1:8443/health"
IFACE = r"\Device\NPF_Loopback"
TSHARK = r"C:\Program Files\Wireshark\tshark.exe"


def https_via_proxy() -> str:
    result = subprocess.run(
        [
            "curl.exe", "-s", "-x", "http://127.0.0.1:8788",
            "-k", TLS_URL, "-w", "HTTP=%{http_code}", "--max-time", "15",
        ],
        capture_output=True, text=True, check=False, timeout=45,
    )
    return result.stdout.strip()


def main() -> int:
    whitelist.assert_loadable()
    proxycheck.proxy_alive_check()
    audit = portaudit.port_bind_audit("artex")
    print(f"[IF-5] artex compliant={audit.compliant}")

    print("[IF-8] capture start (Npcap loopback)")
    session = capture.capture_session("start", IFACE, ROUND_NO)
    print(f"   session={session.session_id[:12]}... pcap={session.pcap_path}")

    engine = DrillEngine()
    engine.start_round(ROUND_NO, total_steps=2)

    print("[step-1] traffic_disguise")
    handle1 = engine.dispatch_task(
        ROUND_NO, 1, TARGET, DrillAction.TRAFFIC_DISGUISE,
        "HTTPS via ARTEX proxy to TLS target (no bare TCP)", TriggerKind.USER_COMMAND,
    )
    out1 = https_via_proxy()
    p1 = round_dir(ROUND_NO) / "step-01-traffic.txt"
    p1.write_text(out1, encoding="utf-8")
    print(f"   {out1}")
    ack1 = engine.report_receipt(
        handle1.handle_id, "success" if "HTTP=200" in out1 else "failure", f"file://{p1}",
        hint="detection: flow appears as TLS session to proxy on target port",
        fact="disguised HTTPS exchange recorded by ARTEX traffic proxy",
    )
    print(f"   ack1={ack1.state_next.value}")

    print("[step-2] heartbeat_sim (3 beats)")
    handle2 = engine.dispatch_task(
        ROUND_NO, 2, TARGET, DrillAction.HEARTBEAT_SIM,
        "3x HTTPS heartbeat, fixed interval", TriggerKind.RECEIPT_EVENT,
    )
    beats = [https_via_proxy() for _ in range(3)]
    p2 = round_dir(ROUND_NO) / "step-02-heartbeats.txt"
    p2.write_text("\n".join(beats), encoding="utf-8")
    for beat in beats:
        print(f"   {beat}")
    ok2 = all("HTTP=200" in beat for beat in beats)
    ack2 = engine.report_receipt(
        handle2.handle_id, "success" if ok2 else "failure", f"file://{p2}",
        hint="detection: fixed-interval TLS sessions to one endpoint = heartbeat signature",
        fact="3 encrypted heartbeats completed",
    )
    print(f"   ack2={ack2.state_next.value}")

    print("[IF-8] capture stop")
    stopped = capture.capture_session("stop", IFACE, ROUND_NO)
    print(f"   pcap={stopped.pcap_path} contiguous={stopped.contiguous}")

    print("[IF-10] pairing checks")
    for step in (1, 2):
        try:
            pair = pairing.pairing_check(step)
            print(f"   step{step}: paired={pair['paired']}")
        except AdapterException as exc:
            print(f"   step{step}: {exc.code.value} -> {exc}")

    print("[IF-9] full verdict (J1~J5 via tshark)")
    counts = verdict.collect_evidence(
        ROUND_NO, str(stopped.pcap_path), tshark_path=TSHARK, audit_available=True
    )
    for key in ("j1_plaintext_hits", "j2_public_ip_hits", "j3_abnormal_outbound",
                "j4_disguise_valid", "j5_log_clean_hits"):
        print(f"   {key} = {counts[key]}")
    report = verdict.verdict_from_counts(ROUND_NO, counts)
    print(f"   CONCLUSION={report['conclusion']} ({report['reason']})")

    print("[round-06 complete]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())