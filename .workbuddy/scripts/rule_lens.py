#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""规矩翻页器 rule_lens.py —— 脑子不背全书，按目录翻页。

四个用法：
  python rule_lens.py list              打印整张目录
  python rule_lens.py need "关键词"      按关键词找这次该读哪几条（只给摘要）
  python rule_lens.py need "关键词" --show  命中后连正文一起翻出来
  python rule_lens.py check             自检：6条是否仍常驻、索引条数对不对

设计要点（缓存友好）：
  每次输出开头都是同一段固定前缀，字字不变；变的部分拼在后面。
  这样前缀稳定，KV Cache 能命中；同一输入永远同一输出。
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INDEX_PATH = os.path.join(ROOT, "rules", "rules_index.json")
FULLTEXT_PATH = os.path.join(ROOT, "rules", "personal_fulltext.md")

# 固定前缀：每次输出都有，字字不动 —— KV Cache 就吃这个
PREFIX = (
    "=== 常驻铁律：6条协作公约（每次会话自动注入，不用翻）===\n"
    "C1全程SDD / C2学习材料 / C3仓库隔离 / C4规矩冻结 / C5执行节制 / C6单一事实源\n"
    "（正文见 .workbuddy/rules/项目协作公约.md，正文一个字没改）\n"
)


def load():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["rules"]


def cmd_list(rules):
    print(PREFIX)
    print("=== 全量目录（按需读，用到哪条翻哪条）===")
    for r in rules:
        if r["layer"] == "ondemand":
            print("[{}] {} — {} — 源:{}".format(
                r["id"], r["title"], r["summary"], r["source"]))
    return 0


def fulltext_for(rule_id):
    """按需翻到正文：个人三层从存档按 ## 标题抽；工作规则/公约指回源文件。"""
    if rule_id.startswith("W"):
        return "（八条正文见 .workbuddy/rules/项目工作规则.md，命中第 {} 条，去读该文件对应编号）".format(rule_id[1:])
    if rule_id.startswith("C"):
        return "（六条常驻，正文见 .workbuddy/rules/项目协作公约.md）"
    if not os.path.exists(FULLTEXT_PATH):
        return "（正文存档缺失：{}）".format(FULLTEXT_PATH)
    with open(FULLTEXT_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    # 找 "## <id> " 开头到下一个 "## " 之间
    m = re.search(r"^## " + re.escape(rule_id) + r"\b.*?(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return "（存档里没找到 {} 的正文）".format(rule_id)
    return m.group(0).strip()


def cmd_need(rules, keywords, show=False):
    # 参数可能一个里带多个词（如 "攻防 靶场"），统一按空格拆开
    kws = []
    for token in keywords:
        kws.extend([w for w in token.split() if w])
    print(PREFIX)
    print("=== 本次任务：{} ===".format(" ".join(kws) if kws else "(无关键词，只给常驻)"))
    if not kws:
        print("没给关键词，只加载 6 条常驻铁律。")
        return 0
    hit = []
    for r in rules:
        if r["layer"] != "ondemand":
            continue
        hay = (r["title"] + " " + r["summary"] + " " + r["when"] + " " + r["source"])
        for kw in kws:
            if kw in hay:
                hit.append(r)
                break
    if not hit:
        print("没匹配到按需规矩，只加载 6 条常驻铁律。")
        return 0
    print("=== 命中 {} 条（按需加载，其余不读）===".format(len(hit)))
    for r in hit:
        print("[{}] {} — {}".format(r["id"], r["title"], r["summary"]))
        if show:
            print("  --- 正文 ---")
            for line in fulltext_for(r["id"]).splitlines():
                print("  " + line)
    return 0


def cmd_check(rules):
    print(PREFIX)
    print("=== 自检 ===")
    constant = [r for r in rules if r["layer"] == "constant"]
    ondemand = [r for r in rules if r["layer"] == "ondemand"]
    ids = [r["id"] for r in rules]
    ok = True
    print("总条数: {} (期望 28)".format(len(rules)))
    print("常驻: {} (期望 6) / 按需: {} (期望 22)".format(len(constant), len(ondemand)))
    print("编号唯一: {}".format("是" if len(ids) == len(set(ids)) else "否"))
    print("6条编号齐全: {}".format("是" if all("C{}".format(i) in ids for i in range(1, 7)) else "否"))
    if len(rules) != 28 or len(constant) != 6 or len(ondemand) != 22:
        ok = False
    if len(ids) != len(set(ids)):
        ok = False
    if not all("C{}".format(i) in ids for i in range(1, 7)):
        ok = False
    print("结论: {}".format("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main():
    rules = load()
    if len(sys.argv) < 2:
        print(__doc__)
        return 0
    cmd = sys.argv[1]
    if cmd == "list":
        return cmd_list(rules)
    if cmd == "need":
        args = sys.argv[2:]
        show = "--show" in args
        args = [a for a in args if a != "--show"]
        return cmd_need(rules, args, show=show)
    if cmd == "check":
        return cmd_check(rules)
    print("未知命令: {}".format(cmd))
    return 2


if __name__ == "__main__":
    sys.exit(main())
