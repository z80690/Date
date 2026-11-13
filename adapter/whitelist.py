"""IF-3 whitelist validation over W1~W5 (design.md 2.2.2, spec 4.3.2-1 / 6.1)."""

from __future__ import annotations

import ipaddress
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from adapter.config import AUDIT_DIR, load_whitelist
from adapter.errors import AdapterException, ErrorCode
from adapter.models import CheckContext, CheckResult

DENY_LOG = AUDIT_DIR / "deny_log.jsonl"


def _load_rules() -> list[tuple[str, list[ipaddress._BaseNetwork]]]:
    """Parse whitelist.json rules into (rule_name, [network]) tuples."""
    data = load_whitelist()
    parsed: list[tuple[str, list[ipaddress._BaseNetwork]]] = []
    for rule in data["rules"]:
        networks = [ipaddress.ip_network(net, strict=False) for net in rule["networks"]]
        parsed.append((rule["name"], networks))
    return parsed


def whitelist_validate(target: str, context: CheckContext) -> CheckResult:
    """Validate a destination address against W1~W5 (IF-3 contract).

    Only IP literals are accepted: resolving a hostname would itself emit a
    DNS query (possible egress), so non-literal targets are denied outright.
    A failed check triggers IF-4 semantics and writes a deny log entry that
    stays queryable via deny_log_id (spec 4.3.2-1 acceptance).
    """
    context_key = context.value if isinstance(context, CheckContext) else str(context)
    try:
        addr = ipaddress.ip_address(target)
    except ValueError:
        return _deny(target, context_key, reason="non_ip_literal")

    for rule_name, networks in _load_rules():
        if any(addr in net for net in networks):
            return CheckResult(passed=True, matched_rule=rule_name)
    return _deny(target, context_key, reason="outside_whitelist")


def _deny(target: str, context_key: str, reason: str) -> CheckResult:
    """Write the intercept log and return a failed result with deny_log_id."""
    entry = {
        "deny_log_id": uuid.uuid4().hex,
        "target": target,
        "context": context_key,
        "reason": reason,
        "captured_at": datetime.now(UTC).isoformat(),
        "outbound_action": "blocked_before_emit",
    }
    DENY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with DENY_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return CheckResult(passed=False, deny_log_id=entry["deny_log_id"])


def read_deny_log(path: Path = DENY_LOG) -> list[dict]:
    """Read back the full deny log (intercept traceability, spec 6.1)."""
    if not path.is_file():
        return []
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def assert_loadable() -> None:
    """Startup guard: whitelist config must load or the drill must not start."""
    try:
        load_whitelist()
    except (FileNotFoundError, ValueError) as exc:
        raise AdapterException(
            ErrorCode.E_WL_CONFIG_MISSING, str(exc)
        ) from exc
