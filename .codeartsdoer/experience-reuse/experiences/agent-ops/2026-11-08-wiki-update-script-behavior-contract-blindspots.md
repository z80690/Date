---
id: 2026-11-08-wiki-update-script-behavior-contract-blindspots
title: Wiki 增量更新脚本链的行为契约与盲区：merge 只覆盖小节、build_index 消费后删 code-links 属正常
category: agent-ops
nature: pitfall
created_at: 2026-11-08T02:46:17
updated_at: 2026-11-08T02:51:21
tags: [脚本契约, 工具盲区, wiki增量更新, 行为验证, 知识库]
keywords: [merge_section_patch, build_index, code-links.json, H1 标题, frontmatter description, 小节合并, title 传播, orphan-page warning, extract_changed_snippets, git diff -U6, changed-files 参数]
problem_patterns:
  - subagent patch 合并回 Wiki 后小节内容已改版，但 H1 标题与 frontmatter description 仍是旧口径，被 build_index 提取为 title 传播到 overview/索引层
  - 脚本消费后删除的中间产物（.code-links.json）被误判为数据丢失或故障，触发不必要的排查
  - 给脚本参数传内联 JSON 字面量被当成文件路径报 FileNotFoundError，不知参数契约是"路径非内容"
source_sessions: [ses_e48b8e01dffeFrd2wwOBkoqJtt]
project: Date
severity: medium
quality_score: 86
hit_count: 1
last_hit_at: 2026-11-08T03:05:16
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wiki-section-revision-patch-json-mode, 2026-11-08-wiki-increment-update-unmatched-file-routing, 2026-11-06-project-knowledge-provenance-format, 2026-11-07-write-receipt-not-proof-of-persistence]
---

# Wiki 增量更新脚本链的行为契约与盲区

## Scenario

以编排者身份执行 Wiki 增量更新的合并与索引阶段：调用 merge_section_patch.py 把 subagent 产出的 patch JSON 合并回 5 篇 Wiki 文档，随后 validate/lint/redact 校验、build_index.py 重建索引与 overview。Agent 不读脚本源码全量、只按 skill 文档调用——脚本的真实行为边界（处理范围、副作用、参数契约）只能靠输出与事后抽查发现。

## Key Signals

- 合并输出 `merged_sections` 只列 `##` 级小节名；合并后抽查发现文档 H1 标题与 frontmatter description 仍是改版前的旧口径（如模块 1 篇→16 篇后 H1 仍写"初始化与目录使用约定"）——merge 的 patch 作用域是 `##` 小节，H1 与 frontmatter 天然不在 patches 的表达范围内。
- extract_changed_snippets 传 `--changed-files "[docs/xxx.md]"` 报 `FileNotFoundError: '[docs/xxx.md]'`——参数期望磁盘上的文件路径，内联 JSON 字面量被原样当路径打开。
- `git diff -U 6` 报 `fatal: bad revision '6'`——`-U` 与上下文行数必须连写 `-U6`，空格形式被 git 解析为两个独立参数（revision）。
- build_index 输出"已删除 5 个 .code-links.json"且 status=success——消费后清理是设计行为，不是数据丢失；同输出的 orphan-page warning 属全量生成遗留的全库性提示，非本轮引入，不阻塞。

## Essence

小节级 patch 合并脚本的作用域边界 = `##` 小节正文；文档级元数据（H1 标题、frontmatter description）是合并链的盲区，必须由编排方在合并后显式补正，否则下游 build_index 从 frontmatter/H1 提取的 title 会把旧口径传播进 wiki-index 与 overview——修订在小节层"成功"而元数据层"漏改"。同时须掌握脚本链的既定副作用与参数契约，把"设计内行为"（code-links 消费即删、遗留 warning）与"真实故障"区分开，避免对正常行为发起错误排查。

## Approach

1. **合并后立即补元数据盲区**：merge 成功后逐篇检查 H1 标题与 frontmatter description 是否与新口径一致；不一致用 edit 手动补正（本例两处：知识库笔记.md 的 description 与 H1），再进入 build_index。
2. **变更行提取走 git diff 直取**：modified 文件的变更对照不传内联 JSON 给 extract_changed_snippets，改用 `git diff -U6 -- <file>`（参数连写）直接取变更行；added 文件直接读全文。
3. **脚本参数先验签名**：调用前用 `-h` 或读脚本 argparse 段确认参数语义（路径 vs 内容、必选 vs 可选）；报 FileNotFoundError 类错误时首先怀疑"传了内容而非路径"。
4. **对脚本副作用先读输出再定性**：build_index 报告删除产物文件且 status=success → 判定为设计内清理，记录后继续；warning 类输出先区分"全库遗留"与"本轮引入"（对比上轮状态），仅后者需处理。
5. **校验链按序全绿才收口**：merge（逐篇 success + merged_sections 符合预期）→ validate_code_links（逐篇 passed）→ lint_wiki（0 errors，warning 记录不阻塞）→ redact_secrets（0 命中）。

## Faster Next Time

- 快捷信号：patch JSON 里没有 H1/frontmatter 字段 → 合并后必查这两处；发现 wiki-index/overview 的 title 带旧口径 → 先查该文档 H1/description 而不是怀疑索引脚本。
- 判定表：`.code-links.json` 消失 + success 输出 = 正常；orphan-page warning + 本轮未新增页面 = 遗留不阻塞；`bad revision 'N'` = git 参数空格拆分；`FileNotFoundError: '[...]'` = 参数应为路径。
- 反模式：合并后直接跑 build_index 不查元数据盲区；把脚本清理行为当异常回滚或重建；对遗留 warning 逐条"修复"造成范围膨胀。

## Applicability Boundaries

- 适用：merge_section_patch/build_index 这类"结构化输入 + 确定性合并"脚本链的使用场景；一般化到任何"patch 合并脚本只覆盖部分文档层"的流程——合并后必须核对未覆盖层。
- 不适用：修订者直接产出 patch 的环节（契约见 wiki-section-revision-patch-json-mode）；全量生成场景（H1/description 由生成流程统一写入，无盲区问题）。
- 平台边界：以本机 CodeArts Agent 沙箱内 system skill 自带 Python 脚本为实证载体；参数契约（路径非内容、-U6 连写）对同名脚本通用。

## Evidence or Examples

- 源会话 ses_e48b8e01dffeFrd2wwOBkoqJtt（docgen-apply，Date 项目）。
- 盲区实证：知识库笔记.md 合并后 5 小节全部 success，但 H1 仍为"知识库笔记（知识库初始化与目录使用约定）"、description 仍为旧口径；手动 edit 补正后 build_index 的 overview 才显示新口径"知识库笔记层：治理机制…"。
- 参数契约实证：`--changed-files "[docs/项目协作公约-最终稿.md]"` → `FileNotFoundError: '[docs/项目协作公约-最终稿.md]'`；`git diff -U 6` → `fatal: bad revision '6'`；改 `git diff -U6` 后正常取到变更行。
- 副作用实证：build_index 输出"已删除 5 个 .code-links.json"+ `{"build_stats": {"reused": 2, "updated": 5, "added": 0, "total": 7}, "code_paths_verified": 77}`，status=success；orphan-page warning 9 条，对比确认全库遗留。