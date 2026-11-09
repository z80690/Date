---
id: 2026-11-08-utf8-nobom-write-verify-first-byte
title: 编码敏感交付物写后必须字节级验证首字节——写回执成功≠无 BOM
category: build-env
nature: pitfall
created_at: 2026-11-08T03:06:16
updated_at: 2026-11-08T03:06:16
tags: [编码, UTF8无BOM, 字节验证, 交付检查, Windows]
keywords: [BOM, EF BB BF, 首字节, Format-Hex, ReadAllBytes, xxd, od, UTF-8 无 BOM, 写后验证, patch JSON]
problem_patterns:
  - 派工要求交付"UTF-8 无 BOM"文件，写工具回执只报成功不报编码，不知道实际落盘是否带 BOM
  - 下游脚本对 BOM 敏感（如 JSON 解析器、gitignore 匹配），带 BOM 交付后可能静默失效或报错
  - 验证"无 BOM"不知道用什么手段，只能靠肉眼看文本内容（看不出来）
source_sessions: [ses_e48be9007ffe3eZZlZ4dLU73sA]
project: Date
severity: medium
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-ps51-getcontent-selectstring-encoding-split, workflow/2026-11-08-wiki-section-revision-patch-json-mode, agent-ops/2026-11-07-write-receipt-not-proof-of-persistence]
---

# 编码敏感交付物写后必须字节级验证首字节——写回执成功≠无 BOM

## Scenario

Windows（PowerShell 5.1）本机交付派工要求"UTF-8，无 BOM"的文件（如供下游合并脚本消费的 patch JSON）。写入工具（write 工具、PowerShell 重定向/Set-Content）回执只报"写入成功"，不报告实际编码；而本机 PS5.1 的写通道历史上有带 BOM 或 UTF-16 落盘的坑（.gitignore 带 BOM 即静默失效）。编码是字节级属性，肉眼看文本内容无法判定。

## Key Signals

- 派工单/契约中出现"UTF-8 无 BOM"字样 → 这是验收字段，不是默认保证。
- 写工具回执 status=success → 只证明持久化（见 write-receipt-not-proof-of-persistence），不证明编码正确。
- 本机已知教训：PS5.1 Out-File 默认 UTF-16LE、部分写法带 BOM；.gitignore 带 BOM 静默失效。
- 读取侧乱码已有专条（ps51-getcontent-selectstring-encoding-split），其边界明确留白"写入侧 BOM 差异是另一问题，不在此展开"——本条正是该留白的填补。

## Essence

"UTF-8 无 BOM"的验证判据是**首字节等于内容首字符的字节编码**：JSON 文件应为 0x7B（`{`），若前缀 EF BB BF 则带 BOM。写回执成功不构成编码证明，交付前必须用字节级手段读取文件头 3 字节做一次判定；带 BOM 时用可显式控制编码的通道重写。

## Approach

1. 写完立即读文件头 3 字节（任选一通道）：
   - PowerShell：`[System.IO.File]::ReadAllBytes($p)[0..2]` 或 `Format-Hex -Path $p -Count 3`
   - bash：`xxd -l 3 $p` 或 `od -An -tx1 -N3 $p`
2. 判定表：JSON 文件头 `7B ...` → 无 BOM，放行；`EF BB BF 7B` → 带 BOM，须重写；`FF FE` → UTF-16LE，编码通道选错。
3. 发现 BOM 的修复：用可显式控制编码的通道重写，如 .NET `[System.IO.File]::WriteAllText($p, $s, [System.Text.UTF8Encoding]::new($false))`（第二参数 false = 无 BOM）。
4. 不要把读取侧乱码误判为文件损坏：无 BOM 中文文件在 PS5.1 Get-Content 默认解码下显示乱码是显示层问题（见 ps51-getcontent-selectstring-encoding-split），与 BOM 与否是两个独立维度。

## Faster Next Time

- 诊断顺序：先读 3 字节，再谈其他；`EF BB BF` 就是 BOM 指纹，见到即判带 BOM。
- 交付 checklist 增项：凡契约写明"UTF-8 无 BOM"的产物，写后 3 字节检查放行才算交付。
- 验证成本极低（一条命令 3 字节），远低于带 BOM 交付后下游脚本静默失效的排查成本。

## Applicability Boundaries

- 适用：Windows + PowerShell 5.1 环境写编码敏感交付物（JSON/配置/gitignore/供脚本消费的中间产物）后的交付前验证。
- 不适用：读取侧解码差异判定（ps51-getcontent-selectstring-encoding-split 已覆盖）；明确允许带 BOM 的场景；PowerShell 7+ 默认写 UTF-8 无 BOM，风险显著降低（但契约验收场景仍建议保留验证习惯）。
- 证据边界：源 trace 仅记录验证输出，未记录具体验证命令；本条命令序列为基于输出的等效实现，未逐一实测。

## Evidence or Examples

- 源会话 ses_e48be9007ffe3eZZlZ4dLU73sA（Wiki 小节修订 subagent，Date 项目）：patch 文件 `.codeartsdoer/temp/wiki-patches/notes_module.json` 写后头部字节验证输出 `7B 0D 0A`（7B=`{`，0D 0A=首行 CRLF），确认无 BOM 前缀，交付放行。
- 关联事实：同项目既有经验 ps51-getcontent-selectstring-encoding-split 在 Applicability Boundaries 中显式留白"写文件时的 BOM/CRLF 行为差异是另一问题，不在此展开"，本条与其构成"写入侧/读取侧"互补对。