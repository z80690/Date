"""安全校验器——三道防线（任务 2.7/2.8）。

第一道：环境就绪校验（受限类目任务启动前，未就绪零动作拒绝）。
第二道：目标与用途越界阻断（目标地址白名单仅本机回环与本机局域网自建资产，
        外部真实目标立即拒绝、告警、落拦截日志）。
第三道：合规完整性校验（四不声明逐项核对、防御配对、工具来源台账）。
全部红线逻辑集中本模块，可审计（spec 4.3、5.5.1 规则 1/2/8）。
"""

from __future__ import annotations

import os
import threading
import time
from typing import Any, Dict, List

FOUR_NO_FIELDS = (
    "no_real_intrusion",
    "no_real_bots",
    "no_real_currency_mixing",
    "no_real_server_hiding",
)
LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")


class SecurityError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class SecurityValidator:
    def __init__(self, store, data_dir: str = ""):
        self._store = store
        self._lock = threading.RLock()
        self._intercept_log_path = os.path.join(data_dir, "intercept_log.jsonl")
        self._declarations: Dict[str, Dict[str, Any]] = {}
        self._scenarios: Dict[str, Dict[str, Any]] = {}
        self._ready_envs: Dict[str, bool] = {}
        self._lan_assets: List[str] = []

    def add_lan_asset(self, host: str) -> None:
        with self._lock:
            self._lan_assets.append(host)

    def set_environment_ready(self, catalog_id: str, ready: bool) -> None:
        with self._lock:
            self._ready_envs[catalog_id] = ready

    def update_declaration_ledger(self, catalog_id: str, declaration: Dict[str, Any]) -> None:
        with self._lock:
            self._declarations[catalog_id] = declaration

    def register_scenario(self, scenario: Dict[str, Any]) -> None:
        with self._lock:
            self._scenarios[scenario["scenario_id"]] = scenario

    def _log_intercept(self, code: str, message: str, context: Dict[str, Any]) -> None:
        entry = {
            "at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "code": code,
            "message": message,
            "context": context,
        }
        with self._lock:
            with open(self._intercept_log_path, "a", encoding="utf-8") as f:
                f.write(_dumps(entry) + "\n")

    def environment_ready(self, catalog_id: str) -> bool:
        with self._lock:
            return bool(self._ready_envs.get(catalog_id, False))

    def check_task(self, catalog_id: str, object_id: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        context = {"catalog_id": catalog_id, "object_id": object_id, "action": action, "params": params}
        is_security_research = bool(params.get("_security_research"))
        if is_security_research:
            if not self.environment_ready(catalog_id):
                msg = "第一道防线：环境就绪校验未通过，受限类目任务零动作拒绝（4.3.1）"
                self._log_intercept("ENV_NOT_READY", msg, context)
                return {"allowed": False, "code": "ENV_NOT_READY", "message": msg}
            scenario = params.get("_scenario") or {}
            for item in scenario.get("required_prepare_items") or []:
                if not self._ready_envs.get(f"prepare:{item}", False):
                    msg = (
                        f"第一道防线联动：环境准备项『{item}』就绪自检未通过，"
                        "对应任务一律拒绝启动（5.2.1 规则 10）"
                    )
                    self._log_intercept("PREPARE_NOT_READY", msg, context)
                    return {"allowed": False, "code": "PREPARE_NOT_READY", "message": msg}
        targets = _collect_targets(params)
        for t in targets:
            host = t.get("host", "")
            if host in LOOPBACK_HOSTS or host in self._lan_assets:
                continue
            msg = f"第二道防线：目标越界 {host} 不在白名单（仅本机回环与本机局域网自建资产），立即拒绝并告警（4.3.2/4.3.3）"
            self._log_intercept("TARGET_OUT_OF_SCOPE", msg, context)
            return {"allowed": False, "code": "TARGET_OUT_OF_SCOPE", "message": msg}
        if is_security_research:
            scenario = params.get("_scenario") or {}
            four_no = scenario.get("four_no_declaration") or {}
            missing = [k for k in FOUR_NO_FIELDS if not four_no.get(k)]
            if missing:
                msg = f"第三道防线：四不声明缺失 {missing}，拒绝执行（4.3.10）"
                self._log_intercept("FOUR_NO_MISSING", msg, context)
                return {"allowed": False, "code": "FOUR_NO_MISSING", "message": msg}
            if not scenario.get("defense_pair_ref"):
                msg = "第三道防线：防御配对缺失，拒绝执行（4.3.5）"
                self._log_intercept("DEFENSE_PAIR_MISSING", msg, context)
                return {"allowed": False, "code": "DEFENSE_PAIR_MISSING", "message": msg}
            if not scenario.get("tools_source_ledger"):
                msg = "第三道防线：工具来源台账缺失，拒绝执行（6.5.7）"
                self._log_intercept("TOOL_LEDGER_MISSING", msg, context)
                return {"allowed": False, "code": "TOOL_LEDGER_MISSING", "message": msg}
        return {"allowed": True, "code": "OK", "message": "三道防线校验通过"}

    def mark_scenario_complete(self, scenario_id: str) -> Dict[str, Any]:
        with self._lock:
            scenario = self._scenarios.get(scenario_id)
            if not scenario:
                raise SecurityError("NOT_FOUND", f"场景不存在: {scenario_id}")
            if not scenario.get("defense_pair_ref"):
                raise SecurityError(
                    "DEFENSE_PAIR_MISSING",
                    "无配对防御产出的场景不得标记为完成（5.5.3 异常 3）",
                )
            scenario["completed"] = True
            return {"scenario_id": scenario_id, "completed": True}

    def intercept_log_tail(self, n: int = 10) -> List[Dict[str, Any]]:
        if not os.path.exists(self._intercept_log_path):
            return []
        with open(self._intercept_log_path, "r", encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        return [_loads(ln) for ln in lines[-n:]]


def _collect_targets(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if "host" in node and isinstance(node["host"], str):
                out.append(node)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(params)
    return out


def _dumps(obj: Dict[str, Any]) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)


def _loads(line: str) -> Dict[str, Any]:
    import json

    return json.loads(line)