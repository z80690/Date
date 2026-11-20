"""核心模块测试：类目注册/调度/回执/环境/安全/门禁/规划/评估/持久化。

按 tasks.md 完成判据逐条覆盖（任务 2.1–2.12）。
"""

from __future__ import annotations

import importlib
import inspect
import json
import os
import pkgutil
import shutil
import tempfile
import time
import unittest
from typing import get_type_hints

from workflow_base.adapters.eval_dims import EMBEDDED_DIMENSIONS
from workflow_base.core.catalog import CatalogError, CatalogRegistry
from workflow_base.core.environment import EnvironmentOrchestrator
from workflow_base.core.evaluator import EvaluatorError, ReportGenerator
from workflow_base.core.gates import APPROVED, REJECTED, WAITING, GateError, GateManager
from workflow_base.core.planner import Planner
from workflow_base.core.receipts import ReceiptCenter, ReceiptError
from workflow_base.core.scheduler import (
    STATUS_FAILED,
    STATUS_INTERRUPTED,
    STATUS_PENDING,
    STATUS_RUNNING,
    STATUS_SUCCESS,
    Scheduler,
    SchedulerError,
)
from workflow_base.core.security import SecurityValidator
from workflow_base.core.store import Store


def noop_contract(info):
    pass


def make_obj(object_id="obj_1", catalog_id="cat_a", actions=None):
    return {
        "object_id": object_id,
        "catalog_id": catalog_id,
        "capability": {
            "actions": actions or [{"name": "do_thing", "params_scope": "*"}],
            "result_types": ["result"],
        },
        "status": "offline",
    }


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.store = Store(self.dir)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class TestCatalog(TempDirTest):
    def _reg(self):
        return CatalogRegistry(self.store)

    def test_mount_and_tree(self):
        reg = self._reg()
        reg.mount({"catalog_id": "cat_a", "name": "A", "parent_id": "ROOT", "implementation_status": "implemented", "env_requirements": "windows"}, noop_contract)
        reg.mount({"catalog_id": "cat_b", "name": "B", "parent_id": "cat_a", "implementation_status": "reserved", "env_requirements": "kali"}, noop_contract)
        tree = reg.tree()
        root = tree["catalogs"][0]
        self.assertEqual(root["catalog_id"], "cat_a")
        self.assertEqual(root["children"][0]["catalog_id"], "cat_b")

    def test_duplicate_rejected_and_original_kept(self):
        reg = self._reg()
        reg.mount({"catalog_id": "cat_a", "name": "A", "parent_id": "ROOT", "implementation_status": "implemented", "env_requirements": "windows"}, noop_contract)
        with self.assertRaises(CatalogError) as ctx:
            reg.mount({"catalog_id": "cat_a", "name": "A2", "parent_id": "ROOT", "implementation_status": "reserved", "env_requirements": "kali"}, noop_contract)
        self.assertEqual(ctx.exception.code, "DUPLICATE_ID")
        self.assertEqual(reg.get("cat_a")["name"], "A")

    def test_parent_missing(self):
        reg = self._reg()
        with self.assertRaises(CatalogError) as ctx:
            reg.mount({"catalog_id": "cat_x", "name": "X", "parent_id": "ghost", "implementation_status": "implemented", "env_requirements": "windows"}, noop_contract)
        self.assertEqual(ctx.exception.code, "PARENT_MISSING")

    def test_incomplete_info_lists_missing(self):
        reg = self._reg()
        with self.assertRaises(CatalogError) as ctx:
            reg.mount({"catalog_id": "cat_y"}, noop_contract)
        self.assertEqual(ctx.exception.code, "INCOMPLETE_INFO")
        self.assertIn("name", ctx.exception.message)

    def test_reserved_start_rejected(self):
        reg = self._reg()
        reg.mount({"catalog_id": "cat_r", "name": "R", "parent_id": "ROOT", "implementation_status": "reserved", "env_requirements": "windows"}, noop_contract)
        with self.assertRaises(CatalogError) as ctx:
            reg.require_implemented("cat_r")
        self.assertEqual(ctx.exception.code, "RESERVED")
        self.assertIn("仅预留接口", ctx.exception.message)


class TestScheduler(TempDirTest):
    def _setup(self, security_ready=True):
        catalog = CatalogRegistry(self.store)
        catalog.mount({"catalog_id": "cat_a", "name": "A", "parent_id": "ROOT", "implementation_status": "implemented", "env_requirements": "windows"}, noop_contract)
        security = SecurityValidator(self.store, self.dir)
        security.set_environment_ready("cat_a", security_ready)
        objects = _ObjectsStub(catalog)
        objects.register(make_obj())
        objects.go_online("obj_1")
        def translator(cid, oid, action, params):
            return {"object_id": oid, "device_command": {"type": action}}
        sched = Scheduler(self.store, catalog, objects, security, translator)
        return sched, objects, security

    def test_out_of_scope_rejected_with_capability_list(self):
        sched, _, _ = self._setup()
        with self.assertRaises(SchedulerError) as ctx:
            sched.start_task("cat_a", "obj_1", "do_other", {})
        self.assertEqual(ctx.exception.code, "ACTION_OUT_OF_SCOPE")
        self.assertIn("do_thing", ctx.exception.message)

    def test_offline_rejected_no_queue(self):
        sched, objects, _ = self._setup()
        objects.go_offline("obj_1")
        with self.assertRaises(SchedulerError) as ctx:
            sched.start_task("cat_a", "obj_1", "do_thing", {})
        self.assertEqual(ctx.exception.code, "OBJECT_OFFLINE")
        self.assertIn("排队", ctx.exception.message)

    def test_unregistered_rejected_zero_action(self):
        sched, _, _ = self._setup()
        with self.assertRaises(SchedulerError) as ctx:
            sched.start_task("cat_a", "ghost", "do_thing", {})
        self.assertEqual(ctx.exception.code, "OBJECT_NOT_REGISTERED")

    def test_state_machine_receipt_only(self):
        sched, _, _ = self._setup()
        task = sched.start_task("cat_a", "obj_1", "do_thing", {})
        tid = task["task_id"]
        self.assertEqual(task["status"], STATUS_RUNNING)
        receipts = ReceiptCenter(self.store, sched)
        receipts.submit(tid, "成功", "done")
        self.assertEqual(sched.query(tid)["status"], STATUS_SUCCESS)
        late = receipts.submit(tid, "失败", "late try")
        self.assertFalse(late["apply"]["accepted"])
        self.assertEqual(sched.query(tid)["status"], STATUS_SUCCESS)

    def test_recheck_not_dangling(self):
        sched, _, _ = self._setup()
        task = sched.start_task("cat_a", "obj_1", "do_thing", {})
        result = sched.recheck(task["task_id"])
        self.assertIn("回执缺失", result["rechecks"][-1]["note"])
        self.assertEqual(result["task"]["status"], STATUS_RUNNING)

    def test_restart_marks_interrupted(self):
        sched, _, _ = self._setup()
        task = sched.start_task("cat_a", "obj_1", "do_thing", {})
        tid = task["task_id"]
        sched2 = Scheduler(self.store, sched._catalogs, sched._objects, sched._security, sched._translator)
        q = sched2.query(tid)
        self.assertEqual(q["status"], STATUS_INTERRUPTED)
        self.assertIn("底座重启", q["reason"])


class _ObjectsStub:
    def __init__(self, catalog):
        self._catalog = catalog
        self._objects = {}

    def register(self, obj):
        self._objects[obj["object_id"]] = obj

    def go_online(self, oid):
        self._objects[oid]["status"] = "online"

    def go_offline(self, oid):
        self._objects[oid]["status"] = "offline"

    def get(self, oid):
        return self._objects.get(oid)


class TestReceipts(TempDirTest):
    def test_empty_conclusion_rejected(self):
        catalog = CatalogRegistry(self.store)
        catalog.mount({"catalog_id": "cat_a", "name": "A", "parent_id": "ROOT", "implementation_status": "implemented", "env_requirements": "windows"}, noop_contract)
        objects = _ObjectsStub(catalog)
        objects.register(make_obj())
        objects.go_online("obj_1")
        sched = Scheduler(self.store, catalog, objects, SecurityValidator(self.store, self.dir), lambda c, o, a, p: {})
        rc = ReceiptCenter(self.store, sched)
        with self.assertRaises(ReceiptError):
            rc.submit("t1", "  ")

    def test_sequential_events(self):
        catalog = CatalogRegistry(self.store)
        catalog.mount({"catalog_id": "cat_a", "name": "A", "parent_id": "ROOT", "implementation_status": "implemented", "env_requirements": "windows"}, noop_contract)
        objects = _ObjectsStub(catalog)
        objects.register(make_obj())
        objects.go_online("obj_1")
        sched = Scheduler(self.store, catalog, objects, SecurityValidator(self.store, self.dir), lambda c, o, a, p: {})
        task = sched.start_task("cat_a", "obj_1", "do_thing", {})
        tid = task["task_id"]
        rc = ReceiptCenter(self.store, sched)
        for i in range(3):
            rc.submit(tid, "成功", f"step{i}", terminal=False)
        events = rc.events_in_order(tid)
        self.assertEqual([e["seq"] for e in events], [1, 2, 3])
        self.assertEqual(sched.query(tid)["status"], STATUS_RUNNING)

    def test_orphan_receipt_no_state_change(self):
        catalog = CatalogRegistry(self.store)
        objects = _ObjectsStub(catalog)
        sched = Scheduler(self.store, catalog, objects, SecurityValidator(self.store, self.dir), lambda c, o, a, p: {})
        rc = ReceiptCenter(self.store, sched)
        notes = []
        sched.set_notifier(notes.append)
        result = rc.submit("no_such_task", "成功", "x")
        self.assertFalse(result["apply"]["accepted"])
        self.assertTrue(result["apply"]["orphan"])
        self.assertTrue(any(n["event"] == "orphan_receipt" for n in notes))


class TestEnvironment(TempDirTest):
    def _setup(self):
        catalog = CatalogRegistry(self.store)
        catalog.mount({"catalog_id": "cat_a", "name": "A", "parent_id": "ROOT", "implementation_status": "implemented", "env_requirements": "windows"}, noop_contract)
        security = SecurityValidator(self.store, self.dir)
        objects = _ObjectsStub(catalog)
        objects.register(make_obj())
        objects.go_online("obj_1")
        objects.register(make_obj("obj_2"))
        objects.go_online("obj_2")
        sched = Scheduler(self.store, catalog, objects, security, lambda c, o, a, p: {})
        env = EnvironmentOrchestrator(self.store, catalog, security, sched)
        return catalog, sched, env, objects

    def test_selfcheck_four_plus_three(self):
        _, _, env, _ = self._setup()
        env.declare_environment("cat_a", {"primary": "windows"})
        report = env.selfcheck()
        self.assertEqual(len(report["checks"]), 4)
        self.assertEqual(len(report["extra_checks"]), 3)
        self.assertTrue(report["all_pass"])

    def test_disconnect_5s_interrupts_and_notifies(self):
        _, sched, env, _ = self._setup()
        notes = []
        env.set_notifier(notes.append)
        env.declare_environment("cat_a", {"primary": "windows"})
        t1 = sched.start_task("cat_a", "obj_1", "do_thing", {})
        env.heartbeat("obj_1")
        env.heartbeat("obj_2")
        now = time.time() + 6
        env.check_timeouts(now)
        q = sched.query(t1["task_id"])
        self.assertEqual(q["status"], STATUS_INTERRUPTED)
        self.assertTrue(any(n["event"] == "disconnect" for n in notes))

    def test_single_instance_isolation(self):
        catalog, sched, env, _ = self._setup()
        env.declare_environment("cat_a", {"primary": "windows"})
        t1 = sched.start_task("cat_a", "obj_1", "do_thing", {})
        env._scheduler.mark_interrupted("obj_1", "模拟崩溃")
        q1 = sched.query(t1["task_id"])
        self.assertEqual(q1["status"], STATUS_INTERRUPTED)
        t2 = sched.start_task("cat_a", "obj_2", "do_thing", {})
        self.assertEqual(t2["status"], STATUS_RUNNING)


class TestSecurity(TempDirTest):
    def test_real_target_blocked_with_log(self):
        sec = SecurityValidator(self.store, self.dir)
        verdict = sec.check_task("cat", "obj", "act", {"endpoint": {"host": "93.184.216.34"}})
        self.assertFalse(verdict["allowed"])
        self.assertEqual(verdict.code if hasattr(verdict, "code") else verdict["code"], "TARGET_OUT_OF_SCOPE")
        tail = sec.intercept_log_tail()
        self.assertTrue(any(e["code"] == "TARGET_OUT_OF_SCOPE" for e in tail))

    def test_loopback_allowed(self):
        sec = SecurityValidator(self.store, self.dir)
        sec.set_environment_ready("cat", True)
        v = sec.check_task("cat", "obj", "act", {"_security_research": True, "endpoint": {"host": "127.0.0.1"}, "_scenario": {
            "four_no_declaration": {k: True for k in ("no_real_intrusion", "no_real_bots", "no_real_currency_mixing", "no_real_server_hiding")},
            "defense_pair_ref": "d1",
            "tools_source_ledger": [{"source": "s", "limited_use": "u"}],
        }})
        self.assertTrue(v["allowed"])

    def test_not_ready_zero_action(self):
        sec = SecurityValidator(self.store, self.dir)
        v = sec.check_task("cat", "obj", "act", {"_security_research": True})
        self.assertFalse(v["allowed"])
        self.assertEqual(v["code"], "ENV_NOT_READY")

    def test_four_no_missing_rejected(self):
        sec = SecurityValidator(self.store, self.dir)
        sec.set_environment_ready("cat", True)
        v = sec.check_task("cat", "obj", "act", {"_security_research": True, "endpoint": {"host": "localhost"}, "_scenario": {
            "four_no_declaration": {"no_real_intrusion": True},
            "defense_pair_ref": "d1",
            "tools_source_ledger": [{"source": "s", "limited_use": "u"}],
        }})
        self.assertEqual(v["code"], "FOUR_NO_MISSING")

    def test_defense_pair_required_for_completion(self):
        sec = SecurityValidator(self.store, self.dir)
        sec.register_scenario({"scenario_id": "s1", "defense_pair_ref": ""})
        with self.assertRaises(Exception):
            sec.mark_scenario_complete("s1")
        sec.register_scenario({"scenario_id": "s2", "defense_pair_ref": "d9"})
        r = sec.mark_scenario_complete("s2")
        self.assertTrue(r["completed"])

    def test_use_out_of_scope_marks_not_ready(self):
        from workflow_base.tools.prepare import PreparePipeline
        pipe = PreparePipeline(sec := SecurityValidator(self.store, self.dir), self.dir)
        r = pipe.enforce_use("tor", "真实外连测试")
        self.assertFalse(r["allowed"])
        self.assertFalse(sec.environment_ready("prepare:tor"))
        tail = sec.intercept_log_tail()
        self.assertTrue(any(e["code"] == "USE_OUT_OF_SCOPE" for e in tail))


class TestGates(TempDirTest):
    def test_skip_stage_rejected(self):
        gm = GateManager(self.store)
        with self.assertRaises(GateError) as ctx:
            gm.submit("execution", "x", allowed_after="spec")
        self.assertEqual(ctx.exception.code, "STAGE_SKIPPED")

    def test_reject_then_resubmit(self):
        gm = GateManager(self.store)
        gm.submit("design", "design.md", allowed_after="spec")
        gm.reject("design", "方案有误，请修订")
        self.assertEqual(gm.all()["design"]["status"], REJECTED)
        self.assertEqual(gm.all()["design"]["reject_opinion"], "方案有误，请修订")
        r = gm.submit("design", "design.md", allowed_after="spec")
        self.assertEqual(r["status"], WAITING)
        gm.confirm("design")
        self.assertTrue(gm.is_approved("design"))

    def test_require_approved_blocks(self):
        gm = GateManager(self.store)
        with self.assertRaises(GateError) as ctx:
            gm.require_approved("tasks")
        self.assertEqual(ctx.exception.code, "GATE_NOT_APPROVED")


class TestPlanner(TempDirTest):
    def test_action_stripped_with_diff_note(self):
        p = Planner(None)
        plan = p.inject("建议整理协议", [{"verb": "执行", "cmd": "rm -rf"}, {"verb": "分析", "cmd": "read"}])
        self.assertEqual(len(plan["stripped_actions"]), 1)
        self.assertIn("剥离", plan["diff_note"])
        self.assertEqual(plan["planning_semantics"][0]["verb"], "分析")

    def test_receipt_authoritative(self):
        p = Planner(None)
        plan = p.inject("建议", [])
        plan["expected_conclusion"] = "成功"
        r = p.compare_with_receipt(plan["plan_id"], "失败", "boom")
        self.assertTrue(r["diff_marked"])
        self.assertEqual(r["authoritative"], "回执")


class TestEvaluator(TempDirTest):
    def test_count_mismatch_rejected(self):
        gen = ReportGenerator(self.store)
        with self.assertRaises(EvaluatorError):
            gen.build_report("embedded", "嵌入式", [{"name": "only_one"}], EMBEDDED_DIMENSIONS, 5)

    def test_premature_decision_rejected(self):
        gen = ReportGenerator(self.store)
        entries = [
            {"name": f"p{i}", "relevance_note": "相关", "scores": {d: {"score": 3, "basis": "b"} for d in EMBEDDED_DIMENSIONS}}
            for i in range(5)
        ]
        entries[0]["note_extra"] = "已选定 x"
        with self.assertRaises(EvaluatorError) as ctx:
            gen.build_report("embedded", "嵌入式", entries, EMBEDDED_DIMENSIONS, 5)
        self.assertEqual(ctx.exception.code, "PREMATURE_DECISION")

    def test_missing_meta_marked_not_fabricated(self):
        gen = ReportGenerator(self.store)
        entries = [{"name": f"p{i}", "relevance_note": "相关"} for i in range(5)]
        report = gen.build_report("embedded", "嵌入式", entries, EMBEDDED_DIMENSIONS, 5)
        self.assertEqual(report["decision_status"], "待用户决策")
        self.assertTrue(report["snapshot_date"])
        for e in report["entries"]:
            for dim, score in e["scores"].items():
                if score["score"] == "无法评估":
                    self.assertIn("不编造", score["basis"])
                    return
        self.fail("expected at least one 无法评估 dimension")


class TestStore(TempDirTest):
    def test_roundtrip_and_version(self):
        self.store.save("catalogs", {"a": 1})
        self.assertEqual(self.store.load("catalogs"), {"a": 1})
        path = os.path.join(self.dir, "catalogs.json")
        with open(path, encoding="utf-8") as f:
            wrapped = json.load(f)
        self.assertEqual(wrapped["format_version"], "v1")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"format_version": "v9", "payload": {}}, f)
        with self.assertRaises(ValueError):
            self.store.load("catalogs")


class TestTypeHintsResolvable(unittest.TestCase):
    """回归守卫：core 包所有类方法的类型注解必须可解析。

    from __future__ import annotations 让注解变成字符串，漏 import 平时不报，
    直到 get_type_hints 才 NameError。这里对每个类方法做一次解析，把这类
    "静默炸弹"变成测试期可见的失败。
    """

    def test_all_core_methods_hints_resolve(self):
        import workflow_base.core as core

        bad = []
        for mod_info in pkgutil.iter_modules(core.__path__):
            mod = importlib.import_module("workflow_base.core." + mod_info.name)
            for _, obj in vars(mod).items():
                if not (inspect.isclass(obj) and obj.__module__ == mod.__name__):
                    continue
                for meth_name, meth in vars(obj).items():
                    if not callable(meth):
                        continue
                    try:
                        get_type_hints(meth)
                    except Exception as exc:  # noqa: BLE001 - 测试需捕获任意解析失败
                        bad.append(f"{mod_info.name}.{obj.__name__}.{meth_name}: {exc}")
        self.assertEqual(bad, [], "类型注解解析失败：\n" + "\n".join(bad))


if __name__ == "__main__":
    unittest.main()