"""底座统一入口（cli）。

组装全部模块；提供自检、默认挂载演示、回环服务启动。
运行方式：cd 02_软件源码 && python -m workflow_base.cli <command>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow_base.core.store import Store
from workflow_base.core.catalog import CatalogRegistry, CatalogError
from workflow_base.core.scheduler import Scheduler, SchedulerError
from workflow_base.core.receipts import ReceiptCenter
from workflow_base.core.environment import EnvironmentOrchestrator
from workflow_base.core.security import SecurityValidator
from workflow_base.core.gates import GateManager
from workflow_base.core.planner import Planner
from workflow_base.core.evaluator import ReportGenerator
from workflow_base.core.server import LoopbackServer
from workflow_base.adapters.contract import validate_catalog_contract
from workflow_base.adapters import embedded, security_research
from workflow_base.adapters.objects import ObjectRegistry


DEFAULT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
LOG_DIR = os.path.join(DEFAULT_ROOT, "04_测试验证")


def multi_translator(catalog_id: str, object_id: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if catalog_id == embedded.CATALOG_ID:
        return embedded.make_translator()(catalog_id, object_id, action, params)
    if catalog_id == security_research.CATALOG_ID:
        return security_research.translate(catalog_id, object_id, action, params)
    raise ValueError(f"该类目无适配翻译规则: {catalog_id}")


class Base:
    """底座组装根。"""

    def __init__(self, data_dir: str = DATA_DIR, log_dir: str = LOG_DIR):
        self.store = Store(data_dir)
        self.catalogs = CatalogRegistry(self.store)
        self.security = SecurityValidator(self.store, data_dir)
        self.objects = ObjectRegistry(self.store, self.catalogs)
        self.scheduler = Scheduler(self.store, self.catalogs, self.objects, self.security, multi_translator)
        self.receipts = ReceiptCenter(self.store, self.scheduler)
        self.environment = EnvironmentOrchestrator(self.store, self.catalogs, self.security, self.scheduler)
        self.gates = GateManager(self.store)
        self.planner = Planner(self.scheduler)
        self.evaluator = ReportGenerator(self.store)
        self.notifications: list = []
        self.scheduler.set_notifier(self.notifications.append)
        self.environment.set_notifier(self.notifications.append)

    def mount_defaults(self) -> Dict[str, Any]:
        mounted = []
        skipped = []
        plans = [
            dict(embedded.CATALOG_CONTRACT),
            dict(security_research.CATALOG_CONTRACT),
            {
                "catalog_id": "appliance_repair",
                "name": "家电维修",
                "parent_id": embedded.CATALOG_ID,
                "implementation_status": "reserved",
                "env_requirements": "windows_or_kali",
                "adapter_kind": "catalog_adapter",
                "receipt_semantics": "预留：待实现后定义",
            },
        ]
        for plan in plans:
            if self.catalogs.get(plan["catalog_id"]):
                skipped.append(plan["catalog_id"])
                continue
            self.catalogs.mount(plan, validate_catalog_contract)
            mounted.append(plan["catalog_id"])
        if not self.catalogs.get(embedded.CATALOG_ID).get("extension_note"):
            self.catalogs.mark_extension(
                embedded.CATALOG_ID,
                "后续阶段：机械臂、水下机器人经同一统一挂载接口接入（扩展接入点预留）",
            )
        if embedded.CATALOG_ID not in self.environment.declarations():
            self.environment.declare_environment(
                embedded.CATALOG_ID, embedded.CATALOG_CONTRACT["env_declaration"]
            )
        if security_research.CATALOG_ID not in self.environment.declarations():
            self.environment.declare_environment(
                security_research.CATALOG_ID, security_research.CATALOG_CONTRACT["env_declaration"]
            )
        return {"mounted": mounted, "skipped_existing": skipped}

    def register_xiaozhi_sim(self, object_id: str = "xiaozhi_sim_01") -> Dict[str, Any]:
        existing = self.objects.get(object_id)
        if existing:
            obj = existing
        else:
            obj = {
                "object_id": object_id,
                "catalog_id": embedded.CATALOG_ID,
                "capability": {
                    "actions": [
                        {"name": "send_text", "params_scope": "text: 非空字符串"},
                        {"name": "report_status", "params_scope": "无参数"},
                    ],
                    "result_types": ["chat_reply", "status"],
                },
                "status": "offline",
            }
            obj = self.objects.register(obj)
        if obj.get("status") != "online":
            self.objects.go_online(object_id, {"env_id": "windows_local_sim", "target_scope": "本机自建资产"})
        self.environment.heartbeat(object_id)
        return self.objects.get(object_id)


def cmd_selfcheck(_: argparse.Namespace) -> None:
    base = Base()
    result = base.environment.selfcheck()
    print(json.dumps(result, ensure_ascii=False, indent=1))
    if not result["all_pass"]:
        sys.exit(1)


def cmd_mount(_: argparse.Namespace) -> None:
    base = Base()
    result = base.mount_defaults()
    print(json.dumps(result, ensure_ascii=False, indent=1))
    print(json.dumps(base.catalogs.tree(), ensure_ascii=False, indent=1))


def cmd_serve(args: argparse.Namespace) -> None:
    base = Base()
    base.mount_defaults()
    dispatcher: Dict[str, Any] = {
        "/catalog/tree": lambda p: base.catalogs.tree(),
        "/selfcheck": lambda p: base.environment.selfcheck(),
        "/task/start": lambda p: base.scheduler.start_task(
            p["catalog_id"], p["object_id"], p["action"], p.get("params", {})
        ),
        "/task/query": lambda p: base.scheduler.query(p["task_id"]),
        "/receipt/submit": lambda p: base.receipts.submit(
            p["task_id"], p["conclusion"], p.get("detail", "")
        ),
    }
    server = LoopbackServer(dispatcher, args.port)
    server.start()
    print(json.dumps({"serving": server.address, "bind": LoopbackServer.bind_description()}, ensure_ascii=False))
    try:
        import time

        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop()


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="workflow_base", description="通用工作流底座")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("selfcheck", help="环境自检（四项必列+三项附加）")
    sub.add_parser("mount", help="挂载默认三类别并展示类目树")
    p_serve = sub.add_parser("serve", help="启动回环服务")
    p_serve.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    {"selfcheck": cmd_selfcheck, "mount": cmd_mount, "serve": cmd_serve}[args.command](args)


if __name__ == "__main__":
    main()