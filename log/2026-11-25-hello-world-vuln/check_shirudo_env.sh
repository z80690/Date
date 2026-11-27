#!/bin/bash
echo "=== quickstart 前置检查 ==="
if [ -r /dev/kvm ] && [ -w /dev/kvm ]; then echo "/dev/kvm 可读写"; else echo "/dev/kvm 不满足"; fi
echo "ulimit -l = $(ulimit -l)"
echo "--- 工具链逐个查 ---"
for t in make pkg-config clang qemu-system-x86 swtpm jq curl dpkg-deb docker gcc llvm-config; do
  p=$(command -v "$t" 2>/dev/null)
  if [ -n "$p" ]; then echo "$t => $p"; else echo "$t => 缺"; fi
done
echo "--- 版本 ---"
openssl version 2>/dev/null || echo "openssl 无"
clang --version 2>/dev/null | head -1 || echo "clang 无"
echo "--- 内核配置 ---"
for k in CONFIG_BPF_SYSCALL CONFIG_BPF_JIT CONFIG_BPF_LSM; do
  v=$(zcat /proc/config.gz 2>/dev/null | grep "^$k=" | head -1)
  echo "${v:-$k 未查到}"
done
