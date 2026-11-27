"""边界护栏：只允许回环地址演练，任何公网 IP（含中国 IP）直接拒绝。
exit 0 = 全部目标合法；exit 2 = 存在非法目标（拒绝执行攻击）。
"""
import ipaddress
import sys

# 演练白名单：仅回环 127.0.0.0/8
ALLOW = [ipaddress.ip_network("127.0.0.0/8")]


def check(targets):
    bad = []
    ok = []
    for t in targets:
        host = t.split(":")[0]
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            bad.append((t, "非 IP（域名/主机名）"))
            continue
        if any(ip in net for net in ALLOW):
            ok.append((t, "PASS 回环地址"))
        else:
            kind = "公网/非回环"
            if ip.is_global:
                kind = "公网 IP（含中国 IP 段）"
            bad.append((t, f"REJECT {kind}"))
    return ok, bad


if __name__ == "__main__":
    targets = sys.argv[1:]
    if not targets:
        print("usage: boundary_guard.py <ip:port> ...")
        sys.exit(3)
    ok, bad = check(targets)
    for t, why in ok:
        print(f"[PASS] {t} {why}")
    for t, why in bad:
        print(f"[REJECT] {t} {why}")
    if bad:
        print(f"RESULT=DENY ({len(bad)} 个目标越界，拒绝执行)")
        sys.exit(2)
    print(f"RESULT=ALLOW ({len(ok)} 个目标均在回环白名单)")
    sys.exit(0)
