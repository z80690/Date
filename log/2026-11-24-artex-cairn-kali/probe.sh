#!/bin/bash
echo "=== 逐跳单层直连探活 ==="
for i in $(seq 0 39); do
  ip="127.0.0.$((i+2))"
  port=$((9000+i))
  code=$(curl -s -m 2 -o /dev/null -w '%{http_code}' "http://$ip:$port/" 2>/dev/null)
  echo "hop$((i+1)) $ip:$port -> $code"
done
echo "=== victim 直连 ==="
curl -s -m 2 -o /dev/null -w 'victim 127.0.0.42:8080 -> %{http_code}\n' http://127.0.0.42:8080/
echo "=== 进程 stat ==="
ps -eo pid,stat,cmd | grep -E 'jump_chain|victim_server' | grep -v grep | head -6
echo "=== 已有chain日志 ==="
ls -la /home/kali/artex-kali-drill/range/artifacts/chain_*.log 2>/dev/null | head -5 || echo none
