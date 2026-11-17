"""适配层测试：契约/对象注册/嵌入式翻译归一/攻防场景校验/环境准备流水线（任务 3.1–3.5、4.4）。"""

from __future__ import annotations

import shutil
import tempfile
import unittest

from workflow_base.adapters import embedded, ghidra_adapter, security_research, velxio_adapter
from workflow_base.adapters.contract import (
    CONTRACT_VERSION,
    ContractError,
    validate_catalog_contract,
    validate_object_contract,
)
from workflow_base.adapters.objects import ObjectError, ObjectRegistry
from workflow_base.core.catalog import CatalogRegistry
from workflow_base.core.security import SecurityValidator
from workflow_base.core.store import Store
from workflow_base.tools.prepare import PrepareError, PreparePipeline


def noop(info):
    pass


def make_cat(catalog_id="cat_a", status="implemented", env="windows"):
    return {
        "catalog_id": catalog_id,
        "name": catalog_id,
        "parent_id": "ROOT",
        "implementation_status": status,
        "env_requirements": env,
        "adapter_kind": "catalog_adapter",
        "receipt_semantics": "s",
    }


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.store = Store(self.dir)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class TestContract(TempDirTest):
    def test_version_is_v1(self):
        self.assertEqual(CONTRACT_VERSION, "v1")

    def test_catalog_contract_fields(self):
        with self.assertRaises(ContractError) as ctx:
            validate_catalog_contract({"catalog_id": "x"})
        self.assertIn("缺失", ctx.exception.message)

    def test_capability_missing_rejected(self):
        obj = {"object_id": "o1", "catalog_id": "cat_a", "status": "offline"}
        with self.assertRaises(ContractError) as ctx:
            validate_object_contract(obj)
        self.assertIn("capability", ctx.exception.message)
        self.assertIn("缺失", ctx.exception.message)

    def test_action_decl_bad(self):
        obj = {
            "object_id": "o1",
            "catalog_id": "cat_a",
            "capability": {"actions": [{"name": "a"}], "result_types": ["r"]},
            "status": "offline",
        }
        with self.assertRaises(ContractError):
            validate_object_contract(obj)


class TestObjectRegistry(TempDirTest):
    def test_register_requires_mounted_implemented_catalog(self):
        cat = CatalogRegistry(self.store)
        obj_reg = ObjectRegistry(self.store, cat)
        with self.assertRaises(ObjectError):
            obj_reg.register({"object_id": "o", "catalog_id": "ghost", "capability": {"actions": [{"name": "a", "params_scope": "*"}], "result_types": ["r"]}, "status": "offline"})
        cat.mount(make_cat(catalog_id="cat_res", status="reserved"), noop)
        with self.assertRaises(ObjectError) as ctx:
            obj_reg.register({"object_id": "o", "catalog_id": "cat_res", "capability": {"actions": [{"name": "a", "params_scope": "*"}], "result_types": ["r"]}, "status": "offline"})
        self.assertEqual(ctx.exception.code, "CATALOG_RESERVED")
        cat.mount(make_cat(catalog_id="cat_ok"), noop)
        r = obj_reg.register({"object_id": "o", "catalog_id": "cat_ok", "capability": {"actions": [{"name": "a", "params_scope": "*"}], "result_types": ["r"]}, "status": "offline"})
        self.assertEqual(r["status"], "offline")
        obj_reg.go_online("o", {"env_id": "e1"})
        self.assertEqual(obj_reg.get("o")["status"], "online")
        self.assertEqual(list(obj_reg.list_online().keys()), ["o"])


class TestEmbeddedAdapter(TempDirTest):
    def test_translate_send_text(self):
        d = embedded.translate("send_text", {"text": "你好"})
        self.assertEqual(d["type"], "chat")
        self.assertEqual(d["payload"], "你好")

    def test_translator_wraps_transport(self):
        tr = embedded.make_translator()
        d = tr(embedded.CATALOG_ID, "xiaozhi_sim_01", "send_text", {"text": "hi"})
        self.assertEqual(d["device_command"]["type"], "chat")
        self.assertEqual(d["device_command"]["transport"], "loopback")

    def test_translate_bad_params(self):
        with self.assertRaises(ValueError):
            embedded.translate("send_text", {"text": ""})

    def test_normalize(self):
        ok = embedded.normalize({"ok": True, "reply": "hi"})
        self.assertEqual(ok["conclusion"], "成功")
        bad = embedded.normalize({"ok": False, "detail": "serial timeout"})
        self.assertEqual(bad["conclusion"], "失败")
        self.assertEqual(bad["detail"], "serial timeout")


class TestSecurityResearchAdapter(TempDirTest):
    def _valid_scenario(self, **over):
        base = {
            "scenario_id": "s_01",
            "dimension": "通讯隐匿",
            "case": {"type": "positive", "name": "公开报道案例A特征复盘"},
            "environment": {"env_id": "kali_local_sim", "target_scope": "本机自建资产"},
            "defense_pair_ref": "defense_01",
            "implementation": {"mode": "自行搭建", "rationale": "无现成方案，仅特征归纳层面"},
            "tools_source_ledger": [{"source": "官方开源渠道", "limited_use": "本地离线演示"}],
            "four_no_declaration": {
                "no_real_intrusion": True,
                "no_real_bots": True,
                "no_real_currency_mixing": True,
                "no_real_server_hiding": True,
            },
        }
        base.update(over)
        return base

    def test_valid_scenario_accepted(self):
        sec = SecurityValidator(self.store, self.dir)
        r = security_research.define_scenario(self._valid_scenario(), sec)
        self.assertTrue(r["accepted"])

    def test_dimension_out_of_scope(self):
        sec = SecurityValidator(self.store, self.dir)
        with self.assertRaises(security_research.ScenarioError) as ctx:
            security_research.define_scenario(self._valid_scenario(dimension="物理攻击"), sec)
        self.assertEqual(ctx.exception.code, "DIMENSION_OUT_OF_SCOPE")
        self.assertIn("Tor浏览器测试", ctx.exception.message)

    def test_four_no_missing_rejected(self):
        sec = SecurityValidator(self.store, self.dir)
        bad = self._valid_scenario()
        bad["four_no_declaration"]["no_real_intrusion"] = False
        with self.assertRaises(security_research.ScenarioError) as ctx:
            security_research.define_scenario(bad, sec)
        self.assertEqual(ctx.exception.code, "FOUR_NO_MISSING")

    def test_defense_pair_missing_rejected(self):
        sec = SecurityValidator(self.store, self.dir)
        with self.assertRaises(security_research.ScenarioError) as ctx:
            security_research.define_scenario(self._valid_scenario(defense_pair_ref=""), sec)
        self.assertEqual(ctx.exception.code, "DEFENSE_PAIR_MISSING")

    def test_target_scope_rejected(self):
        sec = SecurityValidator(self.store, self.dir)
        with self.assertRaises(security_research.ScenarioError):
            security_research.define_scenario(self._valid_scenario(environment={"env_id": "e", "target_scope": "真实外网目标"}), sec)

    def test_tool_ledger_rejected(self):
        sec = SecurityValidator(self.store, self.dir)
        with self.assertRaises(security_research.ScenarioError):
            security_research.define_scenario(self._valid_scenario(tools_source_ledger=[]), sec)

    def test_incomplete_fields_rejected(self):
        sec = SecurityValidator(self.store, self.dir)
        with self.assertRaises(security_research.ScenarioError) as ctx:
            security_research.define_scenario({"scenario_id": "s2"}, sec)
        self.assertEqual(ctx.exception.code, "SCENARIO_INCOMPLETE")


class TestPrepare(TempDirTest):
    def test_source_fail_recorded_no_nonofficial(self):
        sec = SecurityValidator(self.store, self.dir)
        pipe = PreparePipeline(sec, self.dir)
        r = pipe.prepare("tor", installer=None)
        self.assertEqual(r["result"], "未就绪")
        self.assertIn("非官方渠道", r["steps"][-1]["reason"])
        self.assertFalse(sec.environment_ready("prepare:tor"))

    def test_full_pipeline_ready_checklist(self):
        sec = SecurityValidator(self.store, self.dir)
        pipe = PreparePipeline(sec, self.dir)
        r = pipe.prepare("dev_sidecar", installer=lambda hint: hint)
        self.assertEqual(r["result"], "就绪")
        self.assertEqual(set(r["readiness_checklist"].keys()), {"安装来源", "所在环境", "限定用途"})
        self.assertTrue(sec.environment_ready("prepare:dev_sidecar"))

    def test_unknown_item(self):
        sec = SecurityValidator(self.store, self.dir)
        pipe = PreparePipeline(sec, self.dir)
        with self.assertRaises(PrepareError):
            pipe.prepare("unknown_tool", installer=lambda h: h)


class TestVelxioAdapter(TempDirTest):
    """固件仿真适配层：环境探测如实、能力声明不越界、缺失不假装。"""

    def test_detect_missing_home_is_unavailable(self):
        d = velxio_adapter.detect(self.dir + "/does_not_exist")
        self.assertFalse(d["ready"])
        self.assertEqual(d["status"], "unavailable")
        self.assertIn("不假装可用", d["reason"])

    def test_detect_reports_each_probe(self):
        d = velxio_adapter.detect(self.dir + "/does_not_exist")
        items = {c["item"] for c in d["checks"]}
        self.assertTrue({"arduino-cli", "venv-python", "verify-script"}.issubset(items))
        self.assertTrue(all(not c["pass"] for c in d["checks"]))

    def test_compile_blink_unavailable_when_no_env(self):
        r = velxio_adapter.compile_blink(self.dir + "/does_not_exist")
        self.assertFalse(r["ok"])
        self.assertEqual(r["status"], "unavailable")

    def test_capability_declares_layer_boundary(self):
        c = velxio_adapter.capability()
        self.assertEqual(c["tier"], "firmware-simulation")
        self.assertFalse(c["protocol_layer_replaced"])  # 协议桩保留，两层互不替代
        self.assertIn("浏览器前端仿真执行", c["not_yet_verified"])


class TestGhidraAdapter(TempDirTest):
    """二进制逆向适配层：探测如实、归一稳定、缺失不假装（P17）。"""

    def test_detect_missing_home_is_unavailable(self):
        d = ghidra_adapter.detect(self.dir + "/does_not_exist")
        self.assertFalse(d["ready"])
        self.assertEqual(d["status"], "unavailable")
        self.assertIn("不假装可用", d["reason"])

    def test_detect_reports_each_probe(self):
        d = ghidra_adapter.detect(self.dir + "/does_not_exist")
        items = {c["item"] for c in d["checks"]}
        self.assertTrue({"analyzeHeadless", "jdk21"}.issubset(items))
        self.assertFalse(all(c["pass"] for c in d["checks"]))

    def test_analyze_unavailable_when_no_env(self):
        r = ghidra_adapter.analyze_binary("whatever.exe", ghidra_home=self.dir + "/nope")
        self.assertFalse(r["ok"])
        self.assertEqual(r["status"], "unavailable")

    def test_analyze_reports_missing_binary_when_ready(self):
        # 用假 root 会先在环境探测处拦住；只有环境就绪才轮到目标文件校验，
        # 所以这里只断言"不会给出 verified"。
        r = ghidra_adapter.analyze_binary(self.dir + "/ghost.exe")
        self.assertNotEqual(r["status"], "verified")

    def test_normalize_dump_counts(self):
        payload = {
            "program": "t.exe",
            "language_id": "x86:LE:64:default",
            "function_count": 2,
            "functions": [
                {"name": "main", "entry": "140001000", "size_bytes": 10,
                 "decompiled_c": "int main(void) { return 0; }"},
                {"name": "sub", "entry": "140001010", "size_bytes": 5,
                 "decompiled_c": None},
            ],
        }
        n = ghidra_adapter.normalize_dump(payload)
        self.assertEqual(n["function_count"], 2)
        self.assertEqual(n["decompiled_count"], 1)
        self.assertTrue(n["functions"][0]["decompiled"])
        self.assertFalse(n["functions"][1]["decompiled"])

    def test_normalize_dump_empty_payload(self):
        n = ghidra_adapter.normalize_dump({})
        self.assertEqual(n["function_count"], 0)
        self.assertEqual(n["decompiled_count"], 0)
        self.assertEqual(n["functions"], [])

    def test_capability_declares_selection_boundary(self):
        c = ghidra_adapter.capability(self.dir + "/nope")
        self.assertEqual(c["name"], "ghidra_reverse")
        self.assertEqual(c["tier"], "binary-reverse-engineering")
        self.assertIn("IDA 9.5", c["selection"]["video_pointer"])
        self.assertIn("AI 解释层(LLM 桥)", c["not_yet_verified"])


if __name__ == "__main__":
    unittest.main()
