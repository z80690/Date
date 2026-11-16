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
        """固件级仿真接口：Velxio 为推荐执行器（本机实测受限，默认不启用）。

        分层：协议桩（本类 on_command，负责小智会话对答）与固件仿真（本方法）
        是两层，互不替代。Velxio 补的是工作流文档承诺、代码一直空着的固件层。
        """
        return {
            "enabled": False,  # Windows 原生实测 243 失败(pass_fds POSIX 原语)，未达可默认启用门槛
            "note": "固件仿真交给 Velxio（QEMU 跑真固件+串口/GPIO 采集）；协议对端仍走本桩。启用需 Docker 或 WSL Linux 环境",
            "recommended": "davidmonterocrespo24/velxio",
            "license": "AGPLv3（仅本地使用，未修改未分发，不触发传染）",
            "local_path": "D:/refs/velxio",
            "mcp_tools": ["compile_project", "run_project", "create_circuit", "update_circuit"],
            "mcp_transport": "stdio (backend/mcp_server.py) 或 SSE :8002",
            "boards": ["Arduino AVR", "RP2040/Pico", "ESP32(Xtensa/RISC-V)"],
            "measured": {
                "env": "Windows 原生, Python 3.13, pytest 9.2",
                "passed": 1769, "failed": 243, "errors": 8, "skipped": 10,
                "root_cause": "pass_fds not supported on Windows（POSIX fd 传递，QEMU 子进程用）；Arduino 库路径缺失",
                "recommended_runtime": "Docker 镜像 ghcr.io/davidmonterocrespo24/velxio:master 或 WSL Linux",
                "confidence": "L2（单元测试实测；Docker/WSL 路线因 daemon 未起未实测）",
            },
            "legend": {"primary": "velxio", "fallback": "renode/qemu（原规划保留）", "build": "esp-idf/arduino-cli"},
        }