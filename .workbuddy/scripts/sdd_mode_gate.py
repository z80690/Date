#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SDD 双模式触发器：按表判模式，exit code 可判，不靠我主动想起来。

用法：
  python sdd_mode_gate.py "任务描述"        # 判模式
  python sdd_mode_gate.py --self-test       # 自检

退出码：
  0 = sdd（规范驱动开发，默认）
  1 = web-coding（快速通道）
  2 = need-clarify（判不了，问用户）
  3 = 配置/参数错误
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CFG = os.path.join(ROOT, ".workbuddy", "config", "sdd_modes.json")


def load_cfg():
    with open(CFG, "r", encoding="utf-8") as f:
        return json.load(f)


def decide(text, cfg):
    """双命中取 sdd（从严）；零命中取 need-clarify。"""
    sdd = [k for k in cfg["modes"]["sdd"]["trigger_keywords"] if k in text]
    web = [k for k in cfg["modes"]["web_coding"]["trigger_keywords"] if k in text]
    if sdd:
        return 0, "sdd", sdd, web
    if web:
        return 1, "web-coding", sdd, web
    return 2, "need-clarify", sdd, web


def self_test(cfg):
    cases = [
        ("写代码", 0),
        ("重构模块并修bug", 0),
        ("查一下日志", 1),
        ("核对一下规则", 1),
        ("随便做点什么", 2),
        ("写代码顺便查一下", 0),
    ]
    ok = True
    for text, expect in cases:
        code, mode, _, _ = decide(text, cfg)
        flag = "PASS" if code == expect else "FAIL"
        if code != expect:
            ok = False
        print("[{}] {!r} -> {} (期望 {})".format(flag, text, mode, expect))
    print("SELF-TEST: {}".format("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    cfg = load_cfg()
    args = sys.argv[1:]
    if not args:
        print("用法: sdd_mode_gate.py \"任务描述\" | --self-test")
        return 3
    if args[0] == "--self-test":
        return self_test(cfg)
    text = " ".join(args)
    code, mode, sdd_hits, web_hits = decide(text, cfg)
    print(json.dumps({
        "mode": mode,
        "exit": code,
        "sdd_hits": sdd_hits,
        "web_hits": web_hits,
        "default": cfg["default_mode"],
    }, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
