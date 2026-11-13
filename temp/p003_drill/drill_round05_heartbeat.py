"""P003 G4 round-05: heartbeat_sim via ARTEX traffic proxy (3 encrypted beats)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from adapter import pairing, portaudit, proxycheck, whitelist  # noqa: E402
from adapter.config import round_dir  # noqa: E402
from adapter.errors import AdapterException  # noqa: E402
from adapter.models import DrillAction, TriggerKind  # noqa: E402
from adapter.receipt import DrillEngine  # noqa: E402

ROUND_NO = 5
TARGET = "127.0.0.1"
BEATS = 3


def main() -> int:
    whitelist.assert_loadable()
    proxycheck.proxy_alive_check()
    audit = portaudit.port_bind_audit("artex")
    print(f"[IF-5] artex compliant={audit.compliant}")

    engine = DrillEngine()
    engine.start_round(ROUND_NO)
    handle = engine.dispatch_task(
        ROUND_NO,
        1,
        TARGET,
        DrillAction.HEARTBEAT_SIM,
        f"{BEATS}x HTTPS heartbeat via ARTEX proxy (encrypted, no bare TCP)",
        TriggerKind.USER_COMMAND,
    )
    print(f"[IF-1] handle={handle.handle_id[:12]}...")

    outputs = []
    for i in range(BEATS):
        beat = subprocess.run(
            [
                "curl.exe", "-s", "-x", "http://127.0.0.1:8788",
                "-k", "https://127.0.0.1:8443/health",
                "-w", "HTTP=%{http_code}", "--max-time", "15",
            ],
            capture_output=True, text=True, check=False, timeout=45,
        )
        outputs.append(beat.stdout.strip())
        print(f"[beat {i + 1}] {beat.stdout.strip()}")

    hb_path = round_dir(ROUND_NO) / "step-01-heartbeats.txt"
    hb_path.write_text("\n".join(outputs), encoding="utf-8")
    ok = all("HTTP=200" in beat for beat in outputs)
    ack = engine.report_receipt(
        handle.handle_id,
        "success" if ok else "failure",
        f"file://{hb_path}",
        hint="detection: fixed-interval TLS sessions to one endpoint form a heartbeat signature",
        fact=f"{BEATS} encrypted heartbeats completed through ARTEX traffic proxy",
    )
    print(f"[IF-2] state_next={ack.state_next.value}")

    try:
        pair = pairing.pairing_check(1)
        print(f"[IF-10] paired={pair['paired']}")
    except AdapterException as exc:
        print(f"[IF-10] {exc.code.value}: {exc}")

    print("[round-05 complete]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())