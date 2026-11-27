#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SDD 产物门禁：查存在、非空、必填章节、字数、人工扫签收栏。

用法：
  python sdd_artifact_gate.py <产物类型> <文件路径>
  产物类型：spec.md / design.md / tasks.md / apply（支持类型以 sdd_modes.json 为准）

退出码：
  0 = 通过
  1 = 不通过（缺章节/字数不足/人工扫未签收/文件不存在）
  2 = 参数或配置错误
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CFG = os.path.join(ROOT, ".workbuddy", "config", "sdd_modes.json")


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        print("用法: sdd_artifact_gate.py <产物类型> <文件路径>")
        return 2
    kind, path = args
    with open(CFG, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    rule = cfg["artifact_gates"].get(kind)
    if rule is None:
        print("[ERR] 未知产物类型: {}".format(kind))
        return 2
    if not os.path.isfile(path):
        print("[FAIL] 文件不存在: {}".format(path))
        return 1
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    missing = [s for s in rule["required_sections"] if s not in text]
    too_short = len(text) < rule["min_chars"]
    marker = rule.get("human_review_marker")
    no_review = bool(marker) and marker not in text
    if missing:
        print("[FAIL] 缺章节: {}".format("、".join(missing)))
    if too_short:
        print("[FAIL] 字数 {} < {}".format(len(text), rule["min_chars"]))
    if no_review:
        print("[FAIL] 内容偏差人工扫未签收（缺标记: {}）".format(marker))
    if not missing and not too_short and not no_review:
        print("[PASS] {} {} 章节齐( {} ) 字数 {} 人工扫已签收".format(
            kind, path, len(rule["required_sections"]), len(text)))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
