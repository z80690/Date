#!/usr/bin/env python3
"""
CWE-88 参数分隔符注入 · 纯本地教学演示
对照：有病的拼接写法 vs 打补丁后的正确写法
不联网、不碰真实目标、只在本机跑
"""
import subprocess
import shlex


def vulnerable(user_input: str) -> str:
    """有病：把外部输入直接拼进命令字符串，交给 shell 解释"""
    cmd = "echo lookup " + user_input
    # shell=True 让空格/分号被当成命令分隔符 —— 这就是 CWE-88
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return f"命令: {cmd}\n输出: {out.stdout.strip()!r}\n退出码: {out.returncode}"


def patched(user_input: str) -> str:
    """打补丁：参数当成一个整体传，不给 shell 解释的机会"""
    cmd = ["echo", "lookup", user_input]
    out = subprocess.run(cmd, shell=False, capture_output=True, text=True)
    return f"命令: {shlex.join(cmd)}\n输出: {out.stdout.strip()!r}\n退出码: {out.returncode}"


PAYLOAD = "report.txt; echo INJECTED"

if __name__ == "__main__":
    print("=" * 60)
    print("CWE-88 本地演示 —— 参数分隔符被当成新参数")
    print("=" * 60)
    print(f"\n模拟输入（含分号分隔符）: {PAYLOAD!r}\n")

    print("【有病写法 shell=True】")
    print(vulnerable(PAYLOAD))
    print("\n注入生效判定:", "INJECTED" in subprocess.run(
        "echo lookup " + PAYLOAD, shell=True, capture_output=True, text=True
    ).stdout, "\n")

    print("【打补丁后 shell=False + 参数数组】")
    print(patched(PAYLOAD))
    out2 = subprocess.run(["echo", "lookup", PAYLOAD], capture_output=True, text=True)
    print("\n注入生效判定:", "INJECTED" in out2.stdout,
          "（注意：这里出现 INJECTED 只是因为它是字面文本，不是新命令）")

    print("\n" + "=" * 60)
    print("对照结论：有病写法里分号让第二条命令真执行了；补丁写法里它就是个普通字符串。")
