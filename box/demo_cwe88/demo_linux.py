#!/usr/bin/env python3
"""
CWE-88 参数分隔符注入 · 纯本地教学演示（Linux/bash 版）
判据客观化：第二条命令是否真的创建了标记文件，不做字符串匹配。
在 Kali 里跑，不联网、不碰真实目标。
"""
import os
import subprocess
import shlex

MARK = "/tmp/cwe88_injected_marker"
PAYLOAD = f"report.txt; touch {MARK}"


def clean():
    try:
        os.remove(MARK)
    except FileNotFoundError:
        pass


def vulnerable(user_input: str) -> str:
    """有病：外部输入直接拼进命令字符串，交给 shell 解释"""
    cmd = "echo lookup " + user_input
    subprocess.run(cmd, shell=True, capture_output=True, text=True)
    injected = os.path.exists(MARK)
    return f"命令串: {cmd}\n标记文件被创建: {injected}  ← True 即注入真执行了"


def patched(user_input: str) -> str:
    """打补丁：参数当成一个整体传，shell=False"""
    cmd = ["echo", "lookup", user_input]
    subprocess.run(cmd, shell=False, capture_output=True, text=True)
    injected = os.path.exists(MARK)
    return f"命令数组: {shlex.join(cmd)}\n标记文件被创建: {injected}  ← False 即注入没生效"


if __name__ == "__main__":
    print("=" * 60)
    print("CWE-88 本地演示 —— 参数分隔符被当成新参数")
    print("运行于: Linux/bash（分号是真分隔符）")
    print("=" * 60)
    print(f"\n模拟输入: {PAYLOAD!r}\n")

    clean()
    print("【有病写法 shell=True】")
    print(vulnerable(PAYLOAD))

    clean()
    print("\n【打补丁后 shell=False + 参数数组】")
    print(patched(PAYLOAD))

    clean()  # 用完即关：标记文件删掉
    print("\n" + "=" * 60)
    print("对照结论：有病写法里分号让第二条命令真执行（标记文件出现）；")
    print("补丁写法里整串只是一个参数（标记文件不出现）。标记文件已清理。")
