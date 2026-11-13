"""IF-6 proxy process alive check (design.md 2.2.2, spec 5.1.1-2)."""

from __future__ import annotations

import subprocess

from adapter import storage
from adapter.errors import AdapterException, ErrorCode
from adapter.models import AliveResult

_PROXY_IMAGES = ("DevSidecar.exe", "tor.exe", "obfs4proxy.exe")


def _tasklist_image(image: str) -> list[str]:
    """Return running image lines for one process image name."""
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {image}", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, check=False, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdapterException(
            ErrorCode.E_AUDIT_TOOL_MISSING, f"tasklist unavailable: {exc}"
        ) from exc
    return [
        line
        for line in out.stdout.splitlines()
        if line.strip('"').lower().startswith(image.lower())
    ]


def proxy_alive_check(evidence_dir=None) -> AliveResult:
    """Verify Dev-Sidecar/Tor proxy processes are NOT running (IF-6 contract).

    Any alive proxy blocks drill startup with process hints (spec 5.1.3-2);
    none alive releases the drill into environment startup. This check only
    verifies the shutdown state - it never deletes anything (A-1 ruling).
    """
    sidecar_lines = _tasklist_image("DevSidecar.exe")
    tor_lines = [line for image in _PROXY_IMAGES[1:] for line in _tasklist_image(image)]
    hint_parts = [line for line in (*sidecar_lines, *tor_lines) if line.strip()]
    result = AliveResult(
        sidecar_alive=bool(sidecar_lines),
        tor_alive=bool(tor_lines),
        process_hint="\n".join(hint_parts) if hint_parts else None,
    )
    record = {
        "sidecar_alive": result.sidecar_alive,
        "tor_alive": result.tor_alive,
        "process_hint": result.process_hint,
        "gate_pass": not result.sidecar_alive and not result.tor_alive,
    }
    storage.append_record("proxycheck", record, base_dir=evidence_dir)
    if result.sidecar_alive or result.tor_alive:
        raise AdapterException(
            ErrorCode.E_PROXY_STOP_FAILED,
            "live proxy process detected; drill startup blocked",
            detail=record,
        )
    return result
