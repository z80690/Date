"""选型评估报告生成（任务 5.1/5.2/5.3）。

真实拉取 GitHub 公开元数据（公开 API，仅公开页面，4.3.9）；
五维度评分（维度来自适配层配置）；机器自查后落库；
人类可读报告存档 07_参考资料/评估报告/；门禁提交置"等待确认"（G2）。
报告全程不含任何替用户决策的最终选型表述（5.4.1 规则 4）。
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT04 = os.path.join(ROOT, "04_测试验证")
ARCHIVE = os.path.join(ROOT, "07_参考资料", "评估报告")
os.makedirs(OUT04, exist_ok=True)
os.makedirs(ARCHIVE, exist_ok=True)

from workflow_base.cli import Base
from workflow_base.core.evaluator import fetch_repo_meta
from workflow_base.adapters.eval_dims import EMBEDDED_DIMENSIONS, SECURITY_DIMENSIONS

SNAPSHOT = time.strftime("%Y-%m-%d")

EMBEDDED_CANDIDATES = [
    {
        "repo": "78/xiaozhi-esp32",
        "name": "xiaozhi-esp32（小智 ESP32 端）",
        "relevance": "用户指定首个接入实例（小智语音终端）的设备端主项目",
        "scores": {
            "对象抽象与适配模式成熟度": {"score": 4, "basis": "设备端固件采用模块化协议对接（WebSocket/MQTT 会话协议），抽象层成熟；可核对其公开源码结构"},
            "Python生态契合度": {"score": 2, "basis": "设备端为 C++/ESP-IDF 生态，非 Python；Python 契合点在服务端项目（见 xiaozhi-esp32-server 条目）"},
            "社区活跃度": {"score": None, "basis": "以 API 实测 stars/pushed_at 为准（下方元数据）"},
            "向机械臂水下机器人扩展可行性": {"score": 3, "basis": "其会话协议为通用文本/音频指令通道，可作为指令通道复用；但无运动控制抽象，扩展需新增适配层"},
            "许可证与商用限制": {"score": None, "basis": "以 API 实测 license 字段为准"},
        },
    },
    {
        "repo": "xinnan-tech/xiaozhi-esp32-server",
        "name": "xiaozhi-esp32-server（小智服务端）",
        "relevance": "小智生态服务端（Python 主栈），为底座与设备之间的协议枢纽候选",
        "scores": {
            "对象抽象与适配模式成熟度": {"score": 4, "basis": "服务端将设备接入/意图处理/TTS-ASR-LLM 分层，具备可复用接入抽象"},
            "Python生态契合度": {"score": 5, "basis": "Python 实现为主，与本底座 Python 主栈直接契合"},
            "社区活跃度": {"score": None, "basis": "以 API 实测 stars/pushed_at 为准"},
            "向机械臂水下机器人扩展可行性": {"score": 3, "basis": "接入层抽象可平移到其他指令型设备；运动控制/遥测语义需扩展"},
            "许可证与商用限制": {"score": None, "basis": "以 API 实测 license 字段为准"},
        },
    },
    {
        "repo": "renode/renode",
        "name": "Renode（开源 MCU 仿真器）",
        "relevance": "本机仿真环境主候选（Windows 原生运行，支持 STM32/ESP32/RISC-V 无真机仿真）",
        "scores": {
            "对象抽象与适配模式成熟度": {"score": 5, "basis": "平台描述文件+外设模型体系为业界成熟仿真抽象，支持脚本驱动与 UART 日志重定向"},
            "Python生态契合度": {"score": 4, "basis": "内置 Python（IronPython）脚本控制与 Robot 框架集成，可与本底座闭环联动"},
            "社区活跃度": {"score": None, "basis": "以 API 实测 stars/pushed_at 为准"},
            "向机械臂水下机器人扩展可行性": {"score": 4, "basis": "仿真对象=MCU 固件行为，与具体机器人形态解耦，天然可扩展"},
            "许可证与商用限制": {"score": None, "basis": "以 API 实测 license 字段为准"},
        },
    },
    {
        "repo": "espressif/esp-idf",
        "name": "ESP-IDF（ESP32 官方工具链）",
        "relevance": "小智 ESP32 固件的编译构建基础（编译环节必需，Windows 官方支持）",
        "scores": {
            "对象抽象与适配模式成熟度": {"score": 5, "basis": "厂商官方 SDK，构建/组件/驱动抽象完整"},
            "Python生态契合度": {"score": 4, "basis": "构建工具 idf.py 即 Python 实现，Windows 安装器官方支持"},
            "社区活跃度": {"score": None, "basis": "以 API 实测 stars/pushed_at 为准"},
            "向机械臂水下机器人扩展可行性": {"score": 3, "basis": "仅覆盖乐鑫芯片系；其他芯片需换工具链（工具链维度非通用）"},
            "许可证与商用限制": {"score": None, "basis": "以 API 实测 license 字段为准"},
        },
    },
    {
        "repo": "qemu/qemu",
        "name": "QEMU（通用仿真器）",
        "relevance": "本机仿真环境备选（machine 模型可跑部分 ARM 固件，通用性最强）",
        "scores": {
            "对象抽象与适配模式成熟度": {"score": 5, "basis": "业界标准仿真器，机器模型/半虚拟化抽象成熟"},
            "Python生态契合度": {"score": 3, "basis": "主体为 C 实现，Python 仅作外部驱动（QMP/命令行），需自建封装层"},
            "社区活跃度": {"score": None, "basis": "以 API 实测 stars/pushed_at 为准"},
            "向机械臂水下机器人扩展可行性": {"score": 4, "basis": "仿真对象与形态解耦；但 MCU 外设保真度弱于 Renode"},
            "许可证与商用限制": {"score": None, "basis": "以 API 实测 license 字段为准"},
        },
    },
]

SECURITY_CANDIDATES = [
    {
        "repo": "digininja/DVWA",
        "name": "DVWA（ Damn Vulnerable Web Application）",
        "relevance": "官方开源合法靶场典型示例（spec 术语举例），本地离线部署为研究模拟本机自建资产",
        "readiness": "建议用现成",
        "readiness_basis": "官方开源、PHP+MySQL 本机离线部署成熟文档齐备，正/反例研究场景直接可用",
        "scores": {
            "Kali生态契合度": {"score": 5, "basis": "Kali 官方文档含 DVWA 部署指引，生态内事实标准靶场"},
            "本地离线可部署性": {"score": 5, "basis": "本机 Apache+MySQL 即可离线部署，无外部依赖"},
            "社区活跃度": {"score": None, "basis": "以 API 实测 stars/pushed_at 为准"},
            "防御工具覆盖度": {"score": 4, "basis": "漏洞类型覆盖 OWASP 主流类别，可逐类配对防御检测点"},
            "许可证": {"score": None, "basis": "以 API 实测 license 字段为准"},
        },
    },
    {
        "repo": "WebGoat/WebGoat",
        "name": "WebGoat（OWASP 官方靶场）",
        "relevance": "官方开源合法靶场典型示例（Java 系），与 DVWA 互补覆盖不同技术栈",
        "readiness": "建议用现成",
        "readiness_basis": "OWASP 官方维护，jar 单包本机离线运行，课程化场景即取即用",
        "scores": {
            "Kali生态契合度": {"score": 4, "basis": "Kali 可运行（Java 环境），但非 Kali 预装默认项"},
            "本地离线可部署性": {"score": 5, "basis": "官方 jar 本机离线运行，依赖最少"},
            "社区活跃度": {"score": None, "basis": "以 API 实测 stars/pushed_at 为准"},
            "防御工具覆盖度": {"score": 5, "basis": "每课自带防御讲解，攻防配对产出最直接"},
            "许可证": {"score": None, "basis": "以 API 实测 license 字段为准"},
        },
    },
    {
        "repo": "zaproxy/zaproxy",
        "name": "OWASP ZAP",
        "relevance": "白客防御侧主工具候选（扫描/代理/检测），与本底座防御配对产出直接相关",
        "readiness": "建议用现成",
        "readiness_basis": "开源成熟、本机运行、防御检测场景即用",
        "scores": {
            "Kali生态契合度": {"score": 5, "basis": "Kali 预装工具之一"},
            "本地离线可部署性": {"score": 5, "basis": "本机安装即可离线使用（目标仅限本机自建资产）"},
            "社区活跃度": {"score": None, "basis": "以 API 实测 stars/pushed_at 为准"},
            "防御工具覆盖度": {"score": 5, "basis": "以检测/防御视角为核心定位，覆盖度高"},
            "许可证": {"score": None, "basis": "以 API 实测 license 字段为准"},
        },
    },
    {
        "repo": "docmirror/dev-sidecar",
        "name": "开发者边车（dev-sidecar）",
        "relevance": "用户指定准备对象（攻防类目本地代理前置条件），GitHub 官方仓库获取",
        "readiness": "建议用现成",
        "readiness_basis": "官方仓库开源可直接获取；限定用途=本地代理前置条件，禁真实公网穿透",
        "scores": {
            "Kali生态契合度": {"score": 3, "basis": "Windows/Linux 桌面工具，Kali 桌面环境可用但非预装"},
            "本地离线可部署性": {"score": 4, "basis": "本机安装即可；代理范围锁定本机用途"},
            "社区活跃度": {"score": None, "basis": "以 API 实测 stars/pushed_at 为准"},
            "防御工具覆盖度": {"score": 2, "basis": "定位为代理前置条件，非检测/防御工具"},
            "许可证": {"score": None, "basis": "以 API 实测 license 字段为准"},
        },
    },
]


def fetch_all(cands):
    out = []
    for c in cands:
        repo = c["repo"]
        try:
            meta = fetch_repo_meta(repo)
        except Exception as exc:
            meta = {"full_name": repo, "error": str(exc)[:120]}
        out.append({**c, "meta": meta})
    return out


def fill_activity(scores, meta):
    key = [k for k in scores if k == "社区活跃度"][0]
    if "error" in meta:
        scores[key] = {"score": "无法评估", "basis": f"元数据获取失败: {meta['error']}；不编造（5.4.3 异常 3）"}
    else:
        scores[key] = {
            "score": 5 if meta["stars"] > 20000 else 4 if meta["stars"] > 5000 else 3,
            "basis": f"API 实测 stars={meta['stars']}，最近推送={meta['pushed_at']}，open_issues={meta['open_issues']}（快照 {SNAPSHOT}）",
        }
    lic_key = [k for k in scores if k == "许可证"] + [k for k in scores if k == "许可证与商用限制"]
    if lic_key:
        lk = lic_key[0]
        if "error" in meta:
            scores[lk] = {"score": "无法评估", "basis": "元数据获取失败；不编造"}
        else:
            scores[lk] = {"score": 5 if meta["license"] not in (None, "Other") else 2, "basis": f"API 实测 license={meta['license']}"}


def report_text(catalog_label, report):
    lines = [f"# {catalog_label} 选型评估报告（快照日期：{report['snapshot_date']}；决策状态：{report['decision_status']}）", ""]
    for e in report["entries"]:
        lines.append(f"## {e['name']}")
        lines.append(f"- 仓库：{e['meta'].get('html_url') or e['meta'].get('full_name')}")
        if "error" in e["meta"]:
            lines.append(f"- 元数据：获取失败（{e['meta']['error']}）")
        else:
            lines.append(f"- 元数据：stars={e['meta']['stars']}，pushed_at={e['meta']['pushed_at']}，license={e['meta']['license']}")
        if e.get("readiness_conclusion"):
            lines.append(f"- 现成可用性：{e['readiness_conclusion']}（{e['readiness_basis']}）")
        lines.append(f"- 相关性：{e['relevance_note']}")
        lines.append("- 维度评分：")
        for dim, s in e["scores"].items():
            lines.append(f"  - {dim}：{s['score']}（依据：{s['basis']}）")
        lines.append("")
    lines.append("> 本报告为评估结论，不含最终选型；选定由用户拍板（G2 门禁）。")
    return "\n".join(lines)


def main():
    base = Base()
    base.mount_defaults()

    emb = fetch_all(EMBEDDED_CANDIDATES)
    for e in emb:
        fill_activity(e["scores"], e["meta"])
    emb_entries = [
        {
            "name": e["name"],
            "meta": e["meta"],
            "scores": e["scores"],
            "relevance_note": e["relevance"],
        }
        for e in emb
    ]
    rep_emb = base.evaluator.build_report("embedded", "嵌入式开发", emb_entries, EMBEDDED_DIMENSIONS, 5)

    sec = fetch_all(SECURITY_CANDIDATES)
    for e in sec:
        fill_activity(e["scores"], e["meta"])
    sec_entries = [
        {
            "name": e["name"],
            "meta": e["meta"],
            "scores": e["scores"],
            "relevance_note": e["relevance"],
            "readiness_conclusion": e["readiness"],
            "readiness_basis": e["readiness_basis"],
        }
        for e in sec
    ]
    rep_sec = base.evaluator.build_report("security_research", "黑客与白客攻防（研究模拟）", sec_entries, SECURITY_DIMENSIONS, None)

    gate = base.gates.submit("eval_reports", "07_参考资料/评估报告/", allowed_after="tasks")

    os.makedirs(ARCHIVE, exist_ok=True)
    p1 = os.path.join(ARCHIVE, "嵌入式评估报告.md")
    p2 = os.path.join(ARCHIVE, "攻防评估报告.md")
    with open(p1, "w", encoding="utf-8") as f:
        f.write(report_text("嵌入式开发", rep_emb))
    with open(p2, "w", encoding="utf-8") as f:
        f.write(report_text("攻防研究模拟", rep_sec))

    summary = {
        "snapshot_date": SNAPSHOT,
        "embedded_entries": [(e["name"], e["meta"].get("stars"), e["meta"].get("license")) for e in emb],
        "security_entries": [(e["name"], e["meta"].get("stars"), e["meta"].get("license")) for e in sec],
        "decision_status": rep_emb["decision_status"],
        "gate": gate,
        "archive": [p1, p2],
    }
    with open(os.path.join(OUT04, "eval_reports_2026-11-10.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()