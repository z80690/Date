---
id: 2026-11-09-skill-manage-folded-frontmatter-channel-matrix
title: skill_manage 同文件跨 action 对照定位校验器差异：edit 不认折叠样式 frontmatter，patch_frontmatter/patch 可过，write_file 禁写 SKILL.md 本身
category: agent-ops
nature: pitfall
created_at: 2026-11-09T02:05:58
updated_at: 2026-11-09T02:05:58
tags: [skill_manage, frontmatter折叠样式, 通道对照, 工具校验器, 技能演进]
keywords: [skill_manage, description: >-, 折叠样式, YAML folded scalar, patch_frontmatter, action=edit 报错, subpath 白名单, SKILL.md 不可写, 校验器差异, 跨 action 对照实验, 误导性报错, 技能更新]
problem_patterns:
  - 对 description 使用 YAML 折叠样式（`>-`）的已有 SKILL.md 调 skill_manage 的 edit 动作，反复报"SKILL.md must have name and description in frontmatter"而 frontmatter 实际完好，误判为内容问题反复修内容
  - 不确定该用哪个 action 更新技能：改 frontmatter、改正文、整文件重写各自的可用通道不明确，误用 write_file 试图整写 SKILL.md 被白名单拒绝
  - 同一报错在部分 action 上出现、部分 action 上不出现，不知道用对照实验把根因定位到具体校验器
source_sessions: [ses_e4405534affeu8pLGAbuG7Iwh9]
project: Date
severity: medium
quality_score: 91
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-skill-manage-patch-for-partial-edit, 2026-11-07-experience-system-auto-skill-evolution, 2026-11-07-write-receipt-not-proof-of-persistence]
---

# skill_manage 同文件跨 action 对照定位校验器差异：edit 不认折叠样式 frontmatter，patch_frontmatter/patch 可过，write_file 禁写 SKILL.md 本身

## Scenario

后台技能演进流程对 generated-skills 下已有 SKILL.md 做增量更新。该技能的 frontmatter `description` 使用 YAML 折叠样式（`description: >-` 多行折叠），内容完好且此前一直可被 skill_view 正常读回。编排者先用 `action=edit` 做局部修订，连续失败后依次尝试 patch_frontmatter、patch、write_file 三条通道，形成同文件跨 action 对照。

## Key Signals

- `action=edit`（带替换意图的局部 content）连续 4 次报 `SKILL.md must have name and description in frontmatter`——参数形态已换仍同文案失败，且目标 frontmatter 实际完好，报错与文件真实状态矛盾。
- `action=patch_frontmatter`（重写 frontmatter，保留折叠样式）→ `ok:true`，落盘后 skill_view 读回确认折叠样式原样保留。
- `action=patch`（old_string + new_string 修改正文）→ 连续 7 个补丁全部 `ok:true`——同一文件、同一 frontmatter，edit 被拒而 patch 通过。
- `action=write_file` 尝试整写 SKILL.md → 报 `subpath must be in allowed directories: references, examples, scripts, assets`——write_file 的可写子路径白名单不含 SKILL.md 本身。

## Essence

skill_manage 各 action 走**不同的校验路径**：edit 的 frontmatter 校验器按行解析、不认 YAML 折叠样式（`>-`），因此对合法但折叠样式的 frontmatter 误报"缺失"；patch_frontmatter 与 patch 的校验路径能正确处理折叠样式。这修正了此前"edit 是整文件覆盖语义、需传全量 content"的单一解释——即使内容合法，折叠样式本身也会被 edit 的校验器拒绝。对同一文件做跨 action 对照实验，是把"误导性报错"的根因从文件层定位到 action 级校验器的决定性手段。另：write_file 在该工具族中被 subpath 白名单约束，SKILL.md 本身不可整写，只能经由 edit/patch 类动作修改。

## Approach

1. **更新技能的通道决策表**：改 frontmatter → `patch_frontmatter`；改正文局部 → `patch`（old_string/new_string）；新建技能 → `create`；`write_file` 仅用于 references/examples/scripts/assets 子路径资产。
2. **同文案报错 2 次即停止修内容，改做跨 action 对照**：保持目标文件不动，用最小改动依次试探 patch_frontmatter（frontmatter 小改）/ patch（正文小改），哪个通道 ok 即把根因定位到被拒 action 的校验器。
3. **报错文案不作为内容判定依据**："frontmatter 缺失"类报错先核对文件真实状态（skill_view 读回），状态完好即断定校验器误报，切换通道而非重写内容。
4. **ok 回执即权威信号**：patch/patch_frontmatter 返回 `ok:true` 后无需再整文件读回逐字验证（本例读回仅作抽样确认）；对照实验中"成功通道"的输出是根因结论的实证基础。
5. **需要整文件重写 SKILL.md 时**：不要走 write_file（白名单拒绝），用 edit + 全量 content（frontmatter 须为扁平样式）或多次 patch 分段完成。

## Faster Next Time

- 对照矩阵：`description: >-` 折叠样式的 SKILL.md——edit ✗ / patch_frontmatter ✓ / patch ✓ / write_file ✗（白名单）。
- 快捷信号：报错文案指向 frontmatter 但 skill_view 显示 frontmatter 完好 → 校验器误报，立即换 action，禁止第 3 次同参数重试。
- ROI：一次跨 action 对照（2 次调用）即可替代多轮"改内容-重试"循环（本例edit 侧 4 次失败全部可避免）。
- 反模式：把 edit 报错当文件损坏去重写 frontmatter；在 write_file 被白名单拒绝后再试其他路径写 SKILL.md 本身。

## Applicability Boundaries

- 适用：码道 skill_manage 工具族（generated-skills 目录）；frontmatter 含 YAML 折叠样式（`>-`、`|-` 等多行标量）的技能文件更新场景。
- 不适用：文件系统级 Read/Edit/Write 工具（其 edit 是局部替换语义、无 frontmatter 校验，语义与 skill_manage 的 edit 不同）；扁平单行 description 的 SKILL.md 在 edit 下是否能过未实测（推断可过，未复验）。
- 与既有经验分工：`2026-11-07-skill-manage-patch-for-partial-edit` 给出"局部替换用 patch"的决策表并把"edit 需全量 content"列为推断；本条以同文件跨 action 对照实证根因为折叠样式解析差异，并补充 patch_frontmatter 通道与 write_file 白名单两条新边界。"折叠样式是 edit 失败的必要条件"为对照实验支持的强推断，未做扁平样式 edit 的对照复验。

## Evidence or Examples

- 源会话 ses_e4405534affeu8pLGAbuG7Iwh9（docgen-apply fork #1 的 background-evolve-skills 阶段，Date 项目，目标技能 repo-wiki-update-execution）。
- 失败序列实证：edit × 4（两种参数形态）全部报 `SKILL.md must have name and description in frontmatter`；patch_frontmatter × 1 ok；patch × 7（frontmatter 后正文 6 处 + 1 处）全部 ok。
- 折叠样式实证：patch_frontmatter 重写后的 description 仍为 `>-` 折叠块，skill_view 读回内容与预期一致。
- 白名单实证：write_file 报错原文 `subpath must be in allowed directories: references, examples, scripts, assets`。