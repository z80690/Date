"""嵌入式类目适配内容（任务 3.2，小智首例）。

正向翻译（标准任务指令→设备可执行动作）与反向归一（原始结果上报→标准化回执）；
翻译失败兜底（任务标记失败+原因，底座其他功能不受影响，5.3.3 异常 4）。
以注册方式挂载，底座核心零改动（5.3.1 规则 1）。
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

CATALOG_ID = "embedded"
CATALOG_NAME = "嵌入式开发"
CATALOG_CONTRACT = {
    "catalog_id": CATALOG_ID,
    "name": CATALOG_NAME,
    "parent_id": "ROOT",
    "implementation_status": "implemented",
    "env_requirements": "windows_or_kali",
    "adapter_kind": "catalog_adapter",
    "receipt_semantics": "设备侧原始上报经反向归一为 成功/失败 结论的标准回执；结论只认回执",
    "env_declaration": {"primary": "windows", "fallback": "kali"},
}


def translate(action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """正向翻译：标准任务指令 → 设备命令体（type/payload）。

    本函数不依赖任何具体选型实现（G2 门禁前仅做协议级翻译）；
    选型拍板后，6.1 的模拟器宿主按所选项目协议扩展翻译表。
    """
    if action == "send_text":
        text = params.get("text", "")
        if not isinstance(text, str) or not text:
            raise ValueError("send_text 需要 text 字段（非空字符串）")
        return {"type": "chat", "payload": text}
    if action == "report_status":
        return {"type": "status_query", "payload": params}
    raise ValueError(f"未知动作的翻译规则: {action}")


def normalize(raw_report: Dict[str, Any]) -> Dict[str, Any]:
    """反向归一：设备原始结果上报 → 标准化回执（结论 成功/失败 之一）。"""
    ok = bool(raw_report.get("ok", False))
    conclusion = "成功" if ok else "失败"
    detail = str(raw_report.get("detail", "")) or str(raw_report.get("reply", ""))
    return {
        "conclusion": conclusion,
        "detail": detail,
        "raw": raw_report,
    }


def make_translator(simulator_submit: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None):
    """构造挂在调度器受理链上的翻译函数。

    simulator_submit：模拟器宿主提交函数（G2 拍板后由 6.1 提供）；
    未提供时翻译产物仅入队记录，设备命令由演练脚本显式驱动。
    """

    def _translate(catalog_id: str, object_id: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if catalog_id != CATALOG_ID:
            raise ValueError(f"非本类目任务: {catalog_id}")
        cmd = translate(action, params)
        dispatch = {
            "object_id": object_id,
            "device_command": {**cmd, "transport": "loopback"},
            "submit_result": None,
        }
        if simulator_submit is not None:
            dispatch["submit_result"] = simulator_submit(
                {"task_action": action, "params": params}
            )
        return dispatch

    return _translate