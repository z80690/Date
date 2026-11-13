"""评估报告生成器（任务 2.9）。

只读公开元数据检索（GitHub 公开 API，仅公开页面）、五维度评分框架、
机器自查（条目数/禁替用户决策/快照日期/缺失元数据不编造）。
"""

from __future__ import annotations

import json
import time
import urllib.request
from typing import Any, Dict, List, Optional

EMBEDDED_DIMENSIONS_NOTE = "维度清单由调用方（适配层配置）传入，本模块不内置领域维度"
DECISION_PENDING = "待用户决策"
FORBIDDEN_PHRASES = ("已选定", "最终选定为", "推荐采用为最终")

_GH_API = "https://api.github.com"


class EvaluatorError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def fetch_repo_meta(full_name: str) -> Dict[str, Any]:
    url = f"{_GH_API}/repos/{full_name}"
    req = urllib.request.Request(url, headers={"User-Agent": "workflow-base-evaluator", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return {
        "full_name": data.get("full_name"),
        "stars": data.get("stargazers_count"),
        "pushed_at": data.get("pushed_at"),
        "open_issues": data.get("open_issues_count"),
        "license": (data.get("license") or {}).get("spdx_id"),
        "html_url": data.get("html_url"),
        "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


class ReportGenerator:
    def __init__(self, store):
        self._store = store
        self._reports: Dict[str, Dict[str, Any]] = {}
        saved = store.load("reports")
        if saved:
            self._reports = saved

    def _persist(self) -> None:
        self._store.save("reports", self._reports)

    def build_report(self, catalog_id: str, catalog_label: str, entries: List[Dict[str, Any]], dimensions: tuple, expect_count: Optional[int]) -> Dict[str, Any]:
        if expect_count is not None and len(entries) != expect_count:
            raise EvaluatorError(
                "ENTRY_COUNT_MISMATCH",
                f"条目数校验失败: 要求恰好 {expect_count} 个，实际 {len(entries)} 个，拒绝落库（5.4.1 规则 1）",
            )
        snapshot_date = time.strftime("%Y-%m-%d")
        checked: List[Dict[str, Any]] = []
        for e in entries:
            item = dict(e)
            item.setdefault("scores", {})
            for dim in dimensions:
                if dim not in item["scores"]:
                    item["scores"][dim] = {"score": "无法评估", "basis": "元数据获取失败，如实标注，不编造（5.4.3 异常 3）"}
            item.setdefault("relevance_note", "")
            item.setdefault("readiness_conclusion", "")
            checked.append(item)
        report = {
            "catalog_id": catalog_id,
            "catalog_label": catalog_label,
            "decision_status": DECISION_PENDING,
            "snapshot_date": snapshot_date,
            "dimensions": list(dimensions),
            "entries": checked,
        }
        blob = json.dumps(report, ensure_ascii=False)
        for phrase in FORBIDDEN_PHRASES:
            if phrase in blob:
                raise EvaluatorError(
                    "PREMATURE_DECISION",
                    f"报告含替用户决策表述『{phrase}』，拒绝落库（5.4.1 规则 4、6.4.4）",
                )
        key = f"{catalog_id}"
        self._reports[key] = report
        self._persist()
        return report

    def get(self, catalog_id: str) -> Optional[Dict[str, Any]]:
        return self._reports.get(catalog_id)

    def all(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._reports)