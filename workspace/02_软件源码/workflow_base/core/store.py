"""本地持久化与恢复边界（任务 2.12，design D8）。

六类数据资产（类目/实例/回执/报告/门禁/场景）以 JSON v1 落盘；
状态迁移点即时写；执行中中间态不落盘；重启后执行中任务标记中断。
"""

from __future__ import annotations

import json
import os
import threading
from typing import Any, Dict

FORMAT_VERSION = "v1"

_ASSET_KEYS = (
    "catalogs",
    "objects",
    "env_declarations",
    "instances",
    "receipts",
    "reports",
    "gates",
    "scenarios",
)


class Store:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self._lock = threading.RLock()
        os.makedirs(self.data_dir, exist_ok=True)

    def _path(self, name: str) -> str:
        return os.path.join(self.data_dir, f"{name}.json")

    def _events_path(self) -> str:
        return os.path.join(self.data_dir, "events.jsonl")

    def save(self, name: str, payload: Any) -> None:
        import time as _time

        with self._lock:
            if name not in _ASSET_KEYS:
                raise ValueError(f"unknown asset: {name}")
            wrapped = {"format_version": FORMAT_VERSION, "payload": payload}
            tmp = self._path(name) + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(wrapped, f, ensure_ascii=False, indent=1)
            last_error: Exception | None = None
            for _ in range(3):
                try:
                    os.replace(tmp, self._path(name))
                    last_error = None
                    break
                except PermissionError as exc:
                    last_error = exc
                    _time.sleep(0.2)
            if last_error is not None:
                raise last_error

    def load(self, name: str) -> Any:
        with self._lock:
            path = self._path(name)
            if not os.path.exists(path):
                return None
            with open(path, "r", encoding="utf-8") as f:
                wrapped = json.load(f)
            if wrapped.get("format_version") != FORMAT_VERSION:
                raise ValueError(
                    f"format version mismatch in {name}: {wrapped.get('format_version')}"
                )
            return wrapped.get("payload")

    def append_event(self, event: Dict[str, Any]) -> None:
        with self._lock:
            with open(self._events_path(), "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def load_events(self) -> list:
        with self._lock:
            path = self._events_path()
            if not os.path.exists(path):
                return []
            out = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        out.append(json.loads(line))
            return out