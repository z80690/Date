"""Adapter configuration and path layout (design.md 2.3.2/2.3.3)."""

from __future__ import annotations

import json
from pathlib import Path

# Repository root (adapter/ lives one level below it).
REPO_ROOT = Path(__file__).resolve().parent.parent

# Drill evidence base (spec 6.4-1: temp/p003_drill/round-XX/).
DRILL_BASE = REPO_ROOT / "temp" / "p003_drill"
AUDIT_DIR = DRILL_BASE / "audit"

# Whitelist config file (spec 6.1; any change requires user sign-off, spec 6.1-6).
WHITELIST_CONFIG = Path(__file__).resolve().parent / "whitelist.json"

CONTRACT_VERSION = "v1"


def load_whitelist() -> dict:
    """Load W1~W5 whitelist config; abort startup on missing/corrupt file.

    Maps to spec 4.3.2-1 and design IF-3 (E_WL_CONFIG_MISSING blocks startup).
    """
    if not WHITELIST_CONFIG.is_file():
        raise FileNotFoundError(f"whitelist config missing: {WHITELIST_CONFIG}")
    try:
        data = json.loads(WHITELIST_CONFIG.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"whitelist config corrupt: {exc}") from exc
    required = {"version", "rules"}
    if not required.issubset(data):
        raise ValueError(f"whitelist config missing keys: {required - set(data)}")
    return data


def ensure_dirs() -> None:
    """Create the drill evidence directory layout (design 2.3.3)."""
    DRILL_BASE.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def round_dir(round_no: int) -> Path:
    """Return the per-round capture archive directory (spec 6.4-1)."""
    path = DRILL_BASE / f"round-{round_no:02d}"
    path.mkdir(parents=True, exist_ok=True)
    return path
