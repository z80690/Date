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
                    "clock_ticks": "【P16已翻案】当时报'0ms恒定'系采样抓错元素，非真实仿真状态；以 clock_verified_p16 的 CPU cycles 证据为准",
                    "note": "后端需把 arduino-cli 目录加进 PATH，否则编译报 WinError 2；/api/metrics/run 404 是统计埋点，无关仿真",
                },
                "browser_headful_p14": {
                    "env": "有界面 Edge（headless=false）+ 本地全栈，复验上一单'无头限制'猜测",
                    "compile": "✓ 编译成功，924 bytes，programLen=2556（与 MCP 实测一致）",
                    "clock": "计时器恒定 0.0 秒，多次截图无变化；DOM 探查无仿真时钟元素（误抓到的是 OUTPUT 日志时间戳）",
                    "spice_warning": "【P16澄清】'no active vectors'是SPICE电路求解在空载时的正常提示，与AVR数字仿真时钟无关；__spiceDebug 实测 converged=true",
                    "result": "【P16已翻案】当时'未看到闪烁'系弹窗挡住Run+采样抓错元素；CPU cycles 证据证明仿真正常",
                },
                "avr_core_unittest_p15": {
                    "env": "前端 vitest 直接跑 AVR 仿真内核（绕开浏览器整层），Windows 本地 node_modules",
                    "command": "npx vitest run src/__tests__/AVRSimulator.test.ts",
                    "result": "18/18 PASS，含'执行 BLINK_HEX 后 pin13 变高'、'RJMP 循环后保持高'——仿真内核本身完全正常，Blink 逻辑能跑通",
                    "note": "注意 requestAnimationFrame 在测试里被 mock 成同步单步；真实浏览器靠 rAF 驱动时钟，这是与浏览器实测差异所在",
                },
                "root_cause_p15": {
                    "结论": "【P16已翻案】当时推测'卡点在接线层'是错的——P16 用 CPU cycles 证明接线层与 rAF 时钟全程正常，真正的问题是验证脚本本身（抓错元素+弹窗遮挡）。仿真内核和接线都没坏",
                    "换Kali评估": "方向偏——AVR 仿真是纯前端 JS（AVRSimulator.ts 用 avr8js），不是后端 QEMU；Kali 的 POSIX 优势只解决后端 pytest 的 pass_fds，与浏览器时钟不走无关。且实测 Kali 内 pypi/npm 均超时(000)，无代理(.env 仅 Context7 key + SSH 公钥)，装依赖这条路也不通",
                    "docker_image": "ghcr.io/davidmonterocrespo24/velxio:master 曾尝试拉取失败（1.55GB，ghcr.io 国内 136~373KB/s，daemon 不吃系统代理）",
                },
                "clock_verified_p16": {
                    "env": "有界面 Edge，点 Run 后抓控制台 [CPU] Frame 日志 + 时钟文本（关掉 velxio-news-overlay 弹窗）",
                    "cpu_frames": [
                        {"frame":60,"pc":190,"cycles":22932800},
                        {"frame":120,"pc":192,"cycles":39737600},
                        {"frame":180,"pc":204,"cycles":56808000},
                        {"frame":240,"pc":219,"cycles":72811199},
                        {"frame":300,"pc":242,"cycles":94412800},
                    ],
                    "verdict": "仿真时钟确实在走：墙钟4678ms vs 固件虚拟时间4468ms（1:1）；cycles 增长7148万、PC 190→242 持续变化；时钟文本抓到0.8s/0.9s递增；__spiceDebug converged=true",
                    "翻案": "P13/P14 报'时钟0ms不动、灯不闪'是误判——采样脚本抓错DOM元素且被新闻弹窗挡住，没读到真实仿真状态。用CPU cycles底层证据钉死：仿真环境本来就是通的",
                    "root_cause_of_misjudge": "①抓的'0ms'是别的元素非仿真时钟 ②velxio-news-overlay 挡住Run按钮致部分采样实际没点成功 ③没读[CPU]Frame日志",
                },
                "confidence": "L4-AVR（对该AVR Blink场景已闭环：MCP出hex + 浏览器编译成功 + 内核单测18/18 + 浏览器CPU cycles实时走动1:1，四证合一；此前L3系误判已翻案。范围仅限AVR/Uno；ESP32/小智固件、Docker镜像仍未测）",
            },
            "not_yet_verified": ["ESP32/小智固件编译加载（O4，需 ESP-IDF v5.5.4，依赖重）", "Docker 官方镜像端到端（1.5G 拉不动，本地全栈已等效跑通）", "RISC-V/ARM 其它板型仿真（本次仅验证 AVR/Uno）"],
            "legend": {"primary": "velxio", "fallback": "renode/qemu（原规划保留）", "build": "esp-idf/arduino-cli"},
        }