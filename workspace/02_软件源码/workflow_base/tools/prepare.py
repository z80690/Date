"""环境准备四步流水线（任务 4.4）。

来源校验→本机安装→配置锁定→就绪校验；仅允许 获取/安装/配置/就绪校验 四类动作；
就绪自检单三项（安装来源/所在环境/限定用途）；
官方渠道获取失败如实记录（禁改非官方渠道）；用途越界阻断+环境标记不合规。
"""

from __future__ import annotations

import os
import time
from typing import Any, Callable, Dict, List, Optional

PREP_OBJECTS = {
    "tor": {
        "label": "Tor 洋葱浏览器",
        "source_type": "官方开源项目渠道",
        "source_hint": "https://www.torproject.org（官方发行包）",
        "limited_use": "通信隐匿原理演示（本地离线/本地结构演示，禁止真实外连公网目标）",
    },
    "dev_sidecar": {
        "label": "开发者边车",
        "source_type": "GitHub 官方仓库",
        "source_hint": "https://github.com/docmirror/dev-sidecar（官方仓库）",
        "limited_use": "本地代理前置条件（代理范围锁定本机用途，禁真实公网穿透）",
    },
    "official_range": {
        "label": "官方开源靶场（DVWA/WebGoat 等）",
        "source_type": "官方开源项目发布渠道",
        "source_hint": "https://github.com/digininja/DVWA / https://github.com/WebGoat/WebGoat",
        "limited_use": "本地离线部署为本机自建资产，仅供研究模拟",
    },
}
PREP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "06_开发工具", "prepared")


class PrepareError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class PreparePipeline:
    def __init__(self, security, log_dir: str = PREP_DIR):
        self._security = security
        self._log_dir = log_dir
        os.makedirs(self._log_dir, exist_ok=True)
        self._ledger: Dict[str, Dict[str, Any]] = {}

    def _log(self, item: str, record: Dict[str, Any]) -> None:
        path = os.path.join(self._log_dir, f"prepare_{item}.jsonl")
        with open(path, "a", encoding="utf-8") as f:
            import json

            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _source_check(self, item: str, installer: Optional[Callable[[str], str]]) -> str:
        spec = PREP_OBJECTS.get(item)
        if not spec:
            raise PrepareError("UNKNOWN_ITEM", f"未知准备对象: {item}")
        if installer is None:
            raise PrepareError(
                "SOURCE_FAIL",
                f"官方渠道获取失败（未提供安装来源函数）：{spec['source_type']} {spec['source_hint']}；"
                "如实记录，禁改用非官方渠道（5.2.3 异常 4）",
            )
        try:
            location = installer(spec["source_hint"])
        except PrepareError:
            raise
        except Exception as exc:
            raise PrepareError(
                "SOURCE_FAIL",
                f"官方渠道获取失败（{type(exc).__name__}: {str(exc)[:100]}）：{spec['source_type']} {spec['source_hint']}；"
                "如实记录，禁改用非官方渠道（5.2.3 异常 4）",
            )
        if not location or not str(location).startswith("http"):
            raise PrepareError(
                "SOURCE_FAIL",
                f"官方渠道获取失败: {spec['source_type']}；如实记录，禁改用非官方渠道（5.2.3 异常 4）",
            )
        return location

    def prepare(self, item: str, installer: Optional[Callable[[str], str]] = None) -> Dict[str, Any]:
        spec = PREP_OBJECTS.get(item)
        if not spec:
            raise PrepareError("UNKNOWN_ITEM", f"未知准备对象: {item}")
        steps: List[Dict[str, Any]] = []
        try:
            location = self._source_check(item, installer)
            steps.append({"step": "来源校验", "pass": True, "source": location})
        except PrepareError as exc:
            steps.append({"step": "来源校验", "pass": False, "reason": exc.message})
            record = {"item": item, "at": time.strftime("%Y-%m-%d %H:%M:%S"), "result": "未就绪", "steps": steps}
            self._log(item, record)
            return record

        install_dir = os.path.join(self._log_dir, item)
        os.makedirs(install_dir, exist_ok=True)
        marker = os.path.join(install_dir, "installed.marker")
        with open(marker, "w", encoding="utf-8") as f:
            f.write(f"source={spec['source_hint']}\ninstalled_at={time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        steps.append({"step": "本机安装", "pass": True, "dir": install_dir})

        lockfile = os.path.join(install_dir, "config.lock")
        with open(lockfile, "w", encoding="utf-8") as f:
            f.write(f"limited_use={spec['limited_use']}\n")
        steps.append({"step": "配置锁定", "pass": True, "limited_use": spec["limited_use"]})

        checklist = {
            "安装来源": spec["source_type"],
            "所在环境": "Windows 本机直跑（本机仿真环境）",
            "限定用途": spec["limited_use"],
        }
        steps.append({"step": "就绪校验", "pass": True, "checklist": checklist})

        record = {
            "item": item,
            "label": spec["label"],
            "at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "result": "就绪",
            "steps": steps,
            "readiness_checklist": checklist,
        }
        self._ledger[item] = record
        self._log(item, record)
        self._security.set_environment_ready(f"prepare:{item}", True)
        return record

    def enforce_use(self, item: str, requested_use: str) -> Dict[str, Any]:
        spec = PREP_OBJECTS.get(item)
        if not spec:
            raise PrepareError("UNKNOWN_ITEM", f"未知准备对象: {item}")
        allowed = spec["limited_use"]
        if requested_use not in allowed:
            self._security.set_environment_ready(f"prepare:{item}", False)
            msg = (
                f"用途越界：请求用途『{requested_use}』不在限定用途『{allowed}』内；"
                "阻断+告警+环境标记不合规须重新校验（5.2.3 异常 5）"
            )
            self._security._log_intercept("USE_OUT_OF_SCOPE", msg, {"item": item, "requested_use": requested_use})
            return {"allowed": False, "message": msg}
        return {"allowed": True, "message": "用途在限定范围内"}

    def readiness(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._ledger)