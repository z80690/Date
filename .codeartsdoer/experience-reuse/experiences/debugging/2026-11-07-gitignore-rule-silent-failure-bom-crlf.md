---
id: 2026-11-07-gitignore-rule-silent-failure-bom-crlf
title: .gitignore 写入后忽略规则静默失效：BOM/CRLF 混入致模式不匹配，check-ignore 验证加字节级重写
category: debugging
nature: pitfall
created_at: 2026-11-07T05:02:00
updated_at: 2026-11-07T05:02:00
tags: [gitignore, BOM, CRLF, 静默失效, 验证]
keywords: [gitignore 不生效, BOM, CRLF, 字节级写入, git check-ignore, 静默失效, 未跟踪残留, write 工具, 模式匹配, 行尾]
problem_patterns:
  - write 工具写入或追加 .gitignore 后，git status 仍把目标目录/文件列为未跟踪（??）
  - 误判为规则内容写错而反复修改内容，实际根因是 BOM 字节或 CRLF 行尾混入模式导致匹配失败
  - 防护类 ignore 规则（如屏蔽 .env）静默失效未被察觉，敏感文件持续处于暴露状态
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [agent-ops/2026-11-07-sensitive-credential-file-commit-gate-env-block.md, agent-ops/2026-11-06-git-baseline-gitignore-precheck-before-commit-planning.md, debugging/2026-11-06-git-commit-message-mojibake-byte-level-verification.md]
---

# .gitignore 写入后忽略规则静默失效：BOM/CRLF 混入致模式不匹配，check-ignore 验证加字节级重写

## Scenario

提交门禁中为屏蔽敏感文件（.env）与本地状态目录（.obsidian/）向根级 `.gitignore` 追加防护规则并随提交入库；提交完成后复查 `git status`，发现被防护目标仍以未跟踪（??）状态出现——规则疑似没有生效。

## Key Signals

- 规则内容目测完全正确（`.obsidian/`、`.env`），但 ?? 残留；
- `git check-ignore <path>` 对两个目标均无输出（未匹配）——这是判别规则是否真实生效的权威信号；
- 初步怀疑方向（BOM/CRLF 行尾）事后被验证命中：字节级重写后规则立即生效。

## Essence

write 类工具按 UTF-8-BOM/CRLF 写盘时，`.gitignore` 首个模式前混入 BOM 字节、行尾 `\r\n` 被 git 视为模式的一部分，导致所有（或首行）模式静默不匹配。git 对此不报任何错误、不给任何警告——失效只能靠主动验证发现。根因链：写盘工具编码行为 → 文件字节含 BOM/CR → git 模式匹配按字面比较 → 匹配失败 → 防护目标继续暴露。

## Approach

1. `.gitignore` 每次写入/追加后，立即对每个关键模式执行 `git check-ignore <path>`：返回路径 = 生效；无输出 = 失效（当作"ignore 规则的单元测试"）；
2. 确认失效后排查文件字节：BOM 头（EF BB BF）、CRLF 行尾、非 ASCII 字符；
3. 用字节级方式重写（纯 ASCII 内容、LF 行尾、无 BOM）；
4. 重跑 `git check-ignore` 复核每个模式；
5. 修复后的 `.gitignore` 随紧随的提交入库，形成防护闭环。

## Faster Next Time

- 检查顺序：先 `check-ignore` 验证 → 再查字节（BOM/CRLF）→ 最后才怀疑规则语法；多数"不生效"不是语法错而是编码错；
- 防护敏感文件的 ignore 规则必须验证生效——失效即凭据裸奔，风险等级高于普通构建产物泄漏；
- 与提交信息乱码同源：凡经 PowerShell 管道/编码转换的写盘路径，写完即验证，不信任"写入成功"回执。

## Applicability Boundaries

- 适用于 Windows + git（尤其 `core.autocrlf=true` 环境）及可能写 BOM 的写入工具；
- 不适用于规则本身语法错误的情况（如 `.env/` 误写为正则字符未转义）——先验证后查语法，两种失败模式分开处理；
- 对 `.git/info/exclude` 与全局 exclude 文件同样适用（同一匹配引擎）。

## Evidence or Examples

- 本例实测：提交 `da11a01` 后 `git status` 仍显示 `?? .env` 与 `?? .obsidian/`，且 `M .gitignore` 在列；
- 字节级重写 `.gitignore` 后：`check-ignore` 分别返回 `C:\...\Date\.obsidian` 与 `C:\...\Date\.env` = 规则生效；
- 修复随提交 `e02afc3`（3 文件，+66/-5）入库，后续 status 中两目标不再出现。