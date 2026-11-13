"""IF-5 port binding audit (design.md 2.2.2, spec 4.3.2-3)."""

from __future__ import annotations

import ipaddress
import re
import subprocess
from pathlib import Path

from adapter import storage
from adapter.errors import AdapterException, ErrorCode
from adapter.models import BindAuditResult, Listener

# Host addresses that are always compliant (loopback + registered virtual nets).
_ALLOWED_NETS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("192.168.16.0/20"),  # W3: WSL NAT segment (env-ready-trace.md)
]

_NETSTAT_LISTEN = re.compile(r"^\s*(TCP|UDP)\s+([^\s]+):(\d+)\s+[^\s]+:\*\s+LISTENING\s+(\d+)\s*$")


def _framework_pids(framework: str) -> set[int]:
    """Locate the process PIDs of a drill framework via tasklist."""
    if framework == "artex":
        image = "artex.exe"
    elif framework == "cairn":
        image = "cairn-mcp.exe"
    else:
        return set()
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {image}", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, check=False, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdapterException(
            ErrorCode.E_AUDIT_TOOL_MISSING, f"tasklist unavailable: {exc}"
        ) from exc
    pids: set[int] = set()
    for line in out.stdout.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) >= 2 and parts[0].lower() == image.lower():
            try:
                pids.add(int(parts[1]))
            except ValueError:
                continue
    return pids


def _container_ports(framework: str) -> list[Listener]:
    """PentAGI runs as a compose stack; audit its published port mappings."""
    if framework != "pentagi":
        return []
    try:
        out = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Ports}}"],
            capture_output=True, text=True, check=False, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdapterException(
            ErrorCode.E_AUDIT_TOOL_MISSING, f"docker unavailable: {exc}"
        ) from exc
    listeners: list[Listener] = []
    for line in out.stdout.splitlines():
        name, _, ports = line.partition("\t")
        if "pentagi" not in name:
            continue
        for host_side in re.findall(r"([0-9.]+|\[::\]):(\d+)->", ports):
            listeners.append(Listener(addr=host_side[0], port=int(host_side[1])))
    return listeners


def _addr_compliant(addr: str) -> bool:
    """0.0.0.0 / [::] / any wildcard or public address is non-compliant."""
    wildcard = {"0.0.0.0", "::", "*"}
    if addr in wildcard:
        return False
    try:
        ip = ipaddress.ip_address(addr.strip("[]"))
    except ValueError:
        return False
    return any(ip in net for net in _ALLOWED_NETS)


def port_bind_audit(framework: str, evidence_dir: Path | None = None) -> BindAuditResult:
    """Audit every listening endpoint of a framework (IF-5 contract).

    cairn runs over stdio (zero TCP ports) and is compliant by construction.
    Non-compliance (0.0.0.0 / public bind) maps to E_BIND_NON_LOOPBACK with
    block + alert, and the audit lands in the portaudit evidence stream.
    """
    pids = _framework_pids(framework)
    listeners: list[Listener] = list(_container_ports(framework))
    if pids:
        try:
            out = subprocess.run(
                ["netstat", "-ano", "-p", "tcp"],
                capture_output=True, text=True, check=False, timeout=60,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise AdapterException(
                ErrorCode.E_AUDIT_TOOL_MISSING, f"netstat unavailable: {exc}"
            ) from exc
        for line in out.stdout.splitlines():
            match = _NETSTAT_LISTEN.match(line)
            if match and int(match.group(4)) in pids:
                listeners.append(
                    Listener(addr=match.group(2), port=int(match.group(3)), pid=int(match.group(4)))
                )

    compliant = all(_addr_compliant(item.addr) for item in listeners)
    record = {
        "framework": framework,
        "listeners": [item.__dict__ for item in listeners],
        "compliant": compliant,
    }
    record_id = storage.append_record("portaudit", record, base_dir=evidence_dir)
    if not compliant:
        bad = [item for item in listeners if not _addr_compliant(item.addr)]
        raise AdapterException(
            ErrorCode.E_BIND_NON_LOOPBACK,
            f"non-loopback bind on {framework}",
            detail={"audit_record_id": record_id, "offenders": [item.__dict__ for item in bad]},
        )
    return BindAuditResult(listeners=listeners, compliant=compliant)
