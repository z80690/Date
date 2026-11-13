"""JSONL evidence store backing every adapter contract (design.md 2.3.2/2.3.3)."""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path

from adapter.config import AUDIT_DIR

_LOCK = threading.Lock()


def _now() -> str:
    return datetime.now(UTC).isoformat()


def append_record(stream: str, record: dict, base_dir: Path | None = None) -> str:
    """Append one JSONL record to an evidence stream and return its record id.

    Streams: dispatches / receipts / boundary / captures / verdicts / pairings
    / gate / portaudit / proxycheck. Every drill action lands here first -
    this file set is the evidence backbone consumed by IF-9 and IF-10.
    """
    directory = base_dir if base_dir is not None else AUDIT_DIR
    directory.mkdir(parents=True, exist_ok=True)
    record_id = uuid_hex()
    entry = {"record_id": record_id, "recorded_at": _now(), **record}
    path = directory / f"{stream}.jsonl"
    with _LOCK, path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return record_id


def read_stream(stream: str, base_dir: Path | None = None) -> list[dict]:
    """Read back a whole stream (oldest first)."""
    path = (base_dir if base_dir is not None else AUDIT_DIR) / f"{stream}.jsonl"
    if not path.is_file():
        return []
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def uuid_hex() -> str:
    """Short unique id for records/handles."""
    return uuid4_hex()


def uuid4_hex() -> str:
    """Alias kept for testability."""
    import uuid

    return uuid.uuid4().hex


def now_iso() -> str:
    """UTC ISO timestamp used across evidence records."""
    return _now()
