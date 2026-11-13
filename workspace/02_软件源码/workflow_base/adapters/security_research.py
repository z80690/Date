"""攻防类目适配内容（任务 3.3，独立主类目）。

场景定义接口（七项数据字段校验）、维度归属校验、四要素完整性校验；
与安全校验器联动（目标范围越界触发告警+拦截日志）。
全程仅限隔离仿真环境内的研究模拟（四不红线保留）。
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..core.security import FOUR_NO_FIELDS

CATALOG_ID = "security_research"
CATALOG_NAME = "黑客与白客攻防（研究模拟）"
CATALOG_CONTRACT = {
    "catalog_id": CATALOG_ID,
    "name": CATALOG_NAME,
    "parent_id": "ROOT",
    "implementation_status": "implemented",
    "env_requirements": "kali",
    "adapter_kind": "catalog_adapter",
    "receipt_semantics": "模拟场景执行回执=特征归纳与检测思路研究任务的完成结论；攻击侧只到特征归纳层面，配对防御产出必须存在",
    "env_declaration": {"primary": "kali", "fallback": ""},
}

VALID_DIMENSIONS = ("通讯隐匿", "服务器隐匿", "资金安全", "Tor浏览器测试")
SCENARIO_FIELDS = (
    "scenario_id",
    "dimension",
    "case",
    "environment",
    "defense_pair_ref",
    "implementation",
    "tools_source_ledger",
    "four_no_declaration",
)


class ScenarioError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def define_scenario(scenario: Dict[str, Any], security) -> Dict[str, Any]:
    missing = [k for k in SCENARIO_FIELDS if k not in scenario]
    if missing:
        raise ScenarioError(
            "SCENARIO_INCOMPLETE",
            f"场景定义四要素不完整，缺失字段: {missing}（6.5）",
        )
    if scenario["dimension"] not in VALID_DIMENSIONS:
        raise ScenarioError(
            "DIMENSION_OUT_OF_SCOPE",
            f"越出四维度: {scenario['dimension']}；当前支持维度清单: {list(VALID_DIMENSIONS)}（5.5.3 异常 4）",
        )
    case = scenario["case"]
    if not isinstance(case, dict) or case.get("type") not in ("positive", "negative") or not case.get("name"):
        raise ScenarioError(
            "CASE_DECL_BAD",
            "case 须为 {type: positive|negative, name: 公开案例名}（6.5.3）",
        )
    env = scenario["environment"]
    if not isinstance(env, dict) or not env.get("env_id"):
        raise ScenarioError("ENV_DECL_BAD", "environment 须含 env_id（6.5.4）")
    if env.get("target_scope") != "本机自建资产":
        raise ScenarioError(
            "TARGET_SCOPE_BAD",
            "目标范围仅允许 本机自建资产（5.5.1 规则 2、6.5.4）",
        )
    four_no = scenario["four_no_declaration"]
    if not isinstance(four_no, dict) or any(not four_no.get(k) for k in FOUR_NO_FIELDS):
        raise ScenarioError(
            "FOUR_NO_MISSING",
            f"四不声明缺失或不完整: {[k for k in FOUR_NO_FIELDS if not (four_no or {}).get(k)]}（6.5.5）",
        )
    impl = scenario["implementation"]
    if not isinstance(impl, dict) or impl.get("mode") not in ("复用现成", "自行搭建") or not impl.get("rationale"):
        raise ScenarioError(
            "IMPL_DECL_BAD",
            "implementation 须为 {mode: 复用现成|自行搭建, rationale: 依据}（6.5.6、5.5.1 规则 7）",
        )
    ledger = scenario["tools_source_ledger"]
    if not isinstance(ledger, list) or not ledger:
        raise ScenarioError(
            "TOOL_LEDGER_BAD",
            "引用工具必须逐项标注来源渠道与限定用途（6.5.7）",
        )
    for t in ledger:
        if not isinstance(t, dict) or not t.get("source") or not t.get("limited_use"):
            raise ScenarioError(
                "TOOL_LEDGER_BAD",
                "工具来源台账每项须含 source 与 limited_use（6.5.7）",
            )
    if not scenario.get("defense_pair_ref"):
        raise ScenarioError(
            "DEFENSE_PAIR_MISSING",
            "场景必须引用防御配对产出（6.5.5、4.3.5）",
        )
    security.register_scenario(scenario)
    return {"accepted": True, "scenario_id": scenario["scenario_id"]}


def translate(catalog_id: str, object_id: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if catalog_id != CATALOG_ID:
        raise ValueError(f"非本类目任务: {catalog_id}")
    if action != "run_scenario_research":
        raise ValueError(f"攻防类目仅支持 run_scenario_research，收到: {action}")
    scenario_id = params.get("scenario_id")
    if not scenario_id:
        raise ValueError("run_scenario_research 需要 scenario_id")
    return {
        "object_id": object_id,
        "device_command": {
            "type": "scenario_research",
            "payload": {"scenario_id": scenario_id},
            "transport": "loopback",
        },
    }