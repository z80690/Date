#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rule_lens.py 的测试。纯 stdlib，跑法：python test_rule_lens.py"""

import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LENS = os.path.join(HERE, "rule_lens.py")


def run(*args):
    p = subprocess.run([sys.executable, LENS] + list(args),
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout


def check(name, cond):
    print("[{}] {}".format("PASS" if cond else "FAIL", name))
    return cond


def main():
    all_ok = True

    # 1. check 自检
    rc, out = run("check")
    all_ok &= check("check 退出码=0", rc == 0)
    all_ok &= check("check 结论 PASS", "结论: PASS" in out)

    # 2. 前缀稳定：同一输入两次逐字相同
    _, a = run("need", "攻防")
    _, b = run("need", "攻防")
    all_ok &= check("前缀稳定：同输入两次一致", a == b)

    # 3. 前缀跨任务一致（头3行固定）
    _, c = run("need", "攻防")
    _, d = run("need", "编码")
    all_ok &= check("跨任务前缀逐字相同", "\n".join(c.splitlines()[:3]) == "\n".join(d.splitlines()[:3]))

    # 4. 按需命中：不同任务命中不同子集
    _, atk = run("need", "攻防 靶场")
    _, code = run("need", "编码 SDD")
    _, home = run("need", "家电 维修")
    all_ok &= check("攻防命中 W6", "[W6]" in atk)
    all_ok &= check("编码命中 S2-4", "[S2-4]" in code)
    all_ok &= check("家电命中 W5", "[W5]" in home)
    all_ok &= check("按需区分：攻防与编码命中集不同", atk != code)

    # 5. --show 翻到正文
    _, show = run("need", "对齐", "--show")
    all_ok &= check("--show 翻出 S2-2 正文", "概念不一致先停下来确认" in show)

    # 6. 无关键词只给常驻
    _, empty = run("need")
    all_ok &= check("无关键词只加载常驻铁律", "只加载 6 条常驻铁律" in empty)

    print("\n总结: {}".format("全部通过" if all_ok else "有失败项"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
