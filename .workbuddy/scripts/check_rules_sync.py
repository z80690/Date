#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公约三副本一致性校验：码道正本 / .codebuddy / .workbuddy 正文逐字比对。

只抽编号行（如 "7. 预测校正：..."）比对，忽略 frontmatter/标题/来源说明差异。
退出码：0=三份一致；1=有分歧（打印差异）；2=文件缺失。
纯标准库，无定时器、无轮询（公约第 5 条）。
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # .workbuddy/scripts -> 项目根

PATHS = (
    ("码道正本", os.path.join(ROOT, ".codeartsdoer", "rule", "项目协作公约.mdc")),
    ("codebuddy", os.path.join(ROOT, ".codebuddy", "rules", "项目协作公约.md")),
    ("workbuddy", os.path.join(ROOT, ".workbuddy", "rules", "项目协作公约.md")),
)


def numbered_lines(path):
    """抽出所有以 '数字.' 开头的正文行，去掉行尾空白。"""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return tuple(m.group(0).rstrip() for m in re.finditer(r"^\d+\..*$", text, re.M))


def main():
    contents = {}
    for label, path in PATHS:
        if not os.path.isfile(path):
            print("[MISS] {} -> {}".format(label, path))
            return 2
        contents[label] = numbered_lines(path)
        print("[OK] {} : {} 条正文".format(label, len(contents[label])))

    labels = [label for label, _ in PATHS]
    base = contents[labels[0]]
    ok = True
    for label in labels[1:]:
        if contents[label] != base:
            ok = False
            print("[DIFF] {} 与 {} 正文不一致".format(labels[0], label))
            for i in range(max(len(base), len(contents[label]))):
                a = base[i] if i < len(base) else "<无>"
                b = contents[label][i] if i < len(contents[label]) else "<无>"
                if a != b:
                    print("  第{}条  {}: {}".format(i + 1, labels[0], a))
                    print("  第{}条  {}: {}".format(i + 1, label, b))

    if ok:
        print("PASS: 三副本 {} 条正文逐字一致".format(len(base)))
        return 0
    print("FAIL: 三副本存在分歧")
    return 1


if __name__ == "__main__":
    sys.exit(main())
