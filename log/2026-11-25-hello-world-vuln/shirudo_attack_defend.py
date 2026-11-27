#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shirudo 源码级攻防演练
- 防守逻辑照抄 Shirudo 仓库 upatches/java-sql-inj/.../SqlInjectionAdvisor.java 第13-16行
- 正则一字不改: (['\"]\\s*--)|(\\b(OR|AND)\\b\\s+\\d+\\s*=\\s*\\d+)  CASE_INSENSITIVE
- 攻击样本: 咱们第二关 SQL 注入的两种打法
- 跑法: python3 shirudo_attack_defend.py
"""
import re
from urllib.parse import unquote

# === 照抄 Shirudo 的 SQLI_PATTERN（含 CASE_INSENSITIVE）===
SQLI_PATTERN = re.compile(
    r"(['\"]\s*--)|(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
    re.IGNORECASE,
)

# === 模拟第二关靶机的查询拼接 ===
def build_sql(u, p):
    # 真实 Web 拿到参数时会先 URL 解码, 再拼进 SQL。模拟这一步。
    p = unquote(p)
    return f"SELECT * FROM users WHERE username = '{u}' AND password = '{p}'"

# === Shirudo RASP: 在 SQL 发给数据库前拦 ===
def rasp_guard(sql, shield_on):
    if shield_on and SQLI_PATTERN.search(sql):
        return False, "[RASP ALERT] SQL Injection Attempt Detected: " + sql
    return True, "允许执行: " + sql

# === 攻击样本（与第二关实测一致）===
CASES = [
    ("正常登录", "admin", "S3cret!", "应该允许"),
    ("密码栏永真", "admin", "x' OR '1'='1", "应该拦截"),
    ("注释掉密码", "admin' --", "anything", "应该拦截"),
    ("大写绕过尝试", "admin", "x' oR 1=1", "应该拦截"),
    ("AND 恒等式", "admin", "x' AND 1=1", "应该拦截"),
    ("URL编码绕过尝试", "admin", "x%27%20OR%201=1", "看正则是否覆盖"),
    ("换行注释绕过", "admin", "x'\n--", "看正则是否覆盖"),
    ("字符串恒等绕过", "admin", "x' OR 'a'='a", "看正则是否覆盖"),
]

def run(shield_on):
    tag = "盾开启" if shield_on else "盾关闭"
    print(f"===== {tag} =====")
    for name, u, p, expect in CASES:
        sql = build_sql(u, p)
        ok, msg = rasp_guard(sql, shield_on)
        verdict = "拦截" if not ok else "放行"
        print(f"[{name}] 预期={expect} | 实际={verdict}")
        print(f"    SQL: {sql}")
        if not ok:
            print(f"    {msg}")
    print()

if __name__ == "__main__":
    run(False)
    run(True)
