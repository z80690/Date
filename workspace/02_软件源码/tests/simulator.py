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
        """固件级仿真接口：Velxio 为推荐执行器（本地 MCP 编译实测通过，默认启用）。

        分层：协议桩（本类 on_command，负责小智会话对答）与固件仿真（本方法）
        是两层，互不替代。Velxio 补的是工作流文档承诺、代码一直空着的固件层。
        """
        return {
            "enabled": True,  # 本地 venv+arduino-cli+Velxio MCP 实测编 Blink 出 hex，simulation_ready=True
            "note": "固件仿真交给 Velxio（QEMU 跑真固件+串口/GPIO 采集）；协议对端仍走本桩。本地实测走通编译层，仿真执行在浏览器前端",
            "recommended": "davidmonterocrespo24/velxio",
            "license": "AGPLv3（仅本地使用，未修改未分发，不触发传染）",
            "local_path": "D:/refs/velxio",
            "mcp_tools": ["compile_project", "run_project", "create_circuit", "update_circuit"],
            "mcp_transport": "stdio (backend/mcp_server.py) 或 SSE :8002",
            "boards": ["Arduino AVR", "RP2040/Pico", "ESP32(Xtensa/RISC-V)"],
            "runtime": {
                "cli": "D:/refs/velxio/tools/arduino-cli.exe (v1.6.0)",
                "venv": "D:/refs/velxio/.venv",
                "core": "arduino:avr@1.8.8",
                "proxy": "http://127.0.0.1:52764（国内下载 core 必需）",
                "verify_script": "D:/refs/velxio/verify_blink_mcp.py",
            },
            "measured": {
                "native_windows_pytest": {
                    "env": "Windows 原生, Python 3.13, pytest 9.2",
                    "passed": 1769, "failed": 243, "errors": 8, "skipped": 10,
                    "root_cause": "pass_fds not supported on Windows（POSIX fd 传递，QEMU 子进程用）；Arduino 库路径缺失",
                },
                "local_mcp_blink": {
                    "env": "本地 venv + arduino-cli 1.6.0 + Velxio MCP compile_project/run_project",
                    "board": "arduino:avr:uno",
                    "success": True, "simulation_ready": True,
                    "hex_bytes": 2556, "sketch_bytes": 924,
                    "result": "VELXIO_MCP_BLINK PASS",
                },
                "browser_fullstack": {
                    "env": "本地起后端 uvicorn:8001 + 前端 vite:5173，Edge 无头浏览器实测（P13）",
                    "backend": "HTTP 200", "frontend": "HTTP 200",
                    "page_title_ok": True, "console_errors": 0,
                    "click_run": "编译成功（✓ Compilation successful，924 bytes）；日志 programLen=2556 / Loading HEX / Starting AVR simulation；仿真引擎已启动",
                    "clock_ticks": "0ms 恒定（无头浏览器采样 10 次均 0）——仿真时钟未走动，LED 闪烁未看到，不假装已验证",
                    "note": "后端需把 arduino-cli 目录加进 PATH，否则编译报 WinError 2；/api/metrics/run 404 是统计埋点，无关仿真",
                },
                "browser_headful_p14": {
                    "env": "有界面 Edge（headless=false）+ 本地全栈，复验上一单'无头限制'猜测",
                    "compile": "✓ 编译成功，924 bytes，programLen=2556（与 MCP 实测一致）",
                    "clock": "计时器恒定 0.0 秒，多次截图无变化；DOM 探查无仿真时钟元素（误抓到的是 OUTPUT 日志时间戳）",
                    "spice_warning": "SPICE: 目前没有活跃的向量（no active vectors）",
                    "result": "有界面仍未看到 LED 闪烁，排除'无头动画限制'猜测",
                },
                "avr_core_unittest_p15": {
                    "env": "前端 vitest 直接跑 AVR 仿真内核（绕开浏览器整层），Windows 本地 node_modules",
                    "command": "npx vitest run src/__tests__/AVRSimulator.test.ts",
                    "result": "18/18 PASS，含'执行 BLINK_HEX 后 pin13 变高'、'RJMP 循环后保持高'——仿真内核本身完全正常，Blink 逻辑能跑通",
                    "note": "注意 requestAnimationFrame 在测试里被 mock 成同步单步；真实浏览器靠 rAF 驱动时钟，这是与浏览器实测差异所在",
                },
                "root_cause_p15": {
                    "结论": "仿真内核没坏（单测证明）；卡点在浏览器把编译好的 hex 喂给仿真器并驱动 rAF 时钟这一接线层（useSimulatorStore.ts 的 compileBoardProgram/loadHex）",
                    "换Kali评估": "方向偏——AVR 仿真是纯前端 JS（AVRSimulator.ts 用 avr8js），不是后端 QEMU；Kali 的 POSIX 优势只解决后端 pytest 的 pass_fds，与浏览器时钟不走无关。且实测 Kali 内 pypi/npm 均超时(000)，无代理(.env 仅 Context7 key + SSH 公钥)，装依赖这条路也不通",
                    "docker_image": "ghcr.io/davidmonterocrespo24/velxio:master 曾尝试拉取失败（1.55GB，ghcr.io 国内 136~373KB/s，daemon 不吃系统代理）",
                },
                "confidence": "L3（编译层有硬证据：MCP 出 hex + 浏览器编译成功 + 仿真内核单测 18/18；但浏览器端 hex→仿真器接线后时钟不走、LED 闪烁未眼见；ESP32/小智固件未测，不升 L4）",
            },
            "not_yet_verified": ["浏览器里 hex→仿真器接线后为何时钟不走（仿真内核单测已证明正常；疑点在 useSimulatorStore 的 loadHex/rAF 驱动，非 OS 非内核）", "ESP32/小智固件编译加载（O4，需 ESP-IDF）", "Docker 官方镜像端到端"],
            "legend": {"primary": "velxio", "fallback": "renode/qemu（原规划保留）", "build": "esp-idf/arduino-cli"},
        }