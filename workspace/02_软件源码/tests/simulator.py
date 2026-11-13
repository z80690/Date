"""小智模拟器宿主（任务 6.1，G2 拍板后执行）。

选型落位（用户 G2 拍板：嵌入式 5 项全用）：
- 协议参照（服务端）：xinnan-tech/xiaozhi-esp32-server —— 会话指令/上报语义参照（Python 主栈）
- 设备端参照：78/xiaozhi-esp32 —— 设备行为语义参照
- 仿真执行器：Renode（主）/ QEMU（辅）—— 固件级仿真接口预留（real_hardware 路径接入时启用）
- 编译基础：espressif/esp-idf —— 固件构建（真实硬件路径）

形态：协议对等方式模拟设备的指令接收与结果上报（tasks 6.1 允许形态）；
不改任何开源项目源码；模拟器形态与真实硬件形态共用同一套适配契约
（embedded.CATALOG_CONTRACT + capability 三要素）；全程本机回环，无真实外连。
"""

from __future__ import annotations

from typing import Any, Dict, List

SIMULATOR_HOST_CONTRACT_NOTE = (
    "模拟器宿主与真实硬件共用 embedded 类目适配契约（对象级契约三要素一致），"
    "后续真实设备接入仅需替换 object_id 并走同一注册/上线/受理链"
)


class XiaozhiSimulatorHost:
    """协议对等模拟：接收底座翻译后的设备指令，产出原始上报（经适配层反向归一）。"""

    def __init__(self, object_id: str = "xiaozhi_sim_01"):
        self.object_id = object_id
        self.alive = True
        self.received: List[Dict[str, Any]] = []
        self.protocol_ref = {
            "server_semantics": "xiaozhi-esp32-server session protocol (MIT)",
            "device_semantics": "xiaozhi-esp32 device behavior (MIT)",
            "firmware_sim_reserved": ["renode", "qemu"],
            "build_toolchain": "esp-idf",
        }

    def on_command(self, device_command: Dict[str, Any]) -> Dict[str, Any]:
        if not self.alive:
            raise RuntimeError("模拟器宿主已崩溃（异常演练注入）")
        self.received.append(device_command)
        ctype = device_command.get("type")
        if ctype == "chat":
            text = device_command.get("payload", "")
            return {
                "ok": True,
                "reply": f"[xiaozhi-sim] 已响应: {text}",
                "transport": "loopback",
            }
        if ctype == "status_query":
            return {
                "ok": True,
                "reply": "simulator alive; received=%d" % len(self.received),
                "transport": "loopback",
            }
        return {"ok": False, "detail": f"未知指令类型: {ctype}"}

    def crash(self) -> None:
        """异常演练注入：模拟中途崩溃（心跳随之停止）。"""
        self.alive = False

    def firmware_sim_path(self) -> Dict[str, Any]:
        """固件级仿真接口预留：真实硬件路径经 Renode/QEMU 加载固件（本阶段不启用）。"""
        return {
            "enabled": False,
            "note": "协议对等模拟阶段不加载固件；真实硬件接入时经 Renode(主)/QEMU(辅) 加载 ESP-IDF 构建产物",
            "renode": "primary",
            "qemu": "fallback",
            "esp_idf": "build toolchain",
        }