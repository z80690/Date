---
id: 2026-11-13-merge-code-refs-replace-semantics-union-guard
title: 合并脚本 code_refs 替换语义下子集 patch 丢锚：合并前与索引基线做并集保护
category: workflow
nature: pitfall
created_at: 2026-11-13T11:48:45
updated_at: 2026-11-13T11:57:27
tags: [patch合并, code_refs, 替换语义, 并集保护, 锚点保全]
keywords: [merge_section_patch, code_refs 替换语义, 子集 patch, 空列表清空, 并集保护预处理, wiki-index 基线, 原锚点丢失, 同名文件新行号整体替换, 短路径后缀映射, 无行号锚剔除, build_index 验证]
problem_patterns:
  - "subagent 返回的 code_refs 是索引基线的子集甚至空列表，直接交给替换语义的合并脚本会静默丢失原锚点"
  - "未读合并脚本源码就消费 patch，不知道 code_refs 是替换还是合并语义，凭 patch 结构猜不出来"
  - "patch 内引用路径丢目录前缀、混入无行号且基线不存在的锚，合并后溯源链污染"
source_sessions: [ses_e2d0191d6ffejSEq6m0pmTb0hf]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-09-subagent-patch-code-refs-baseline-fallback, 2026-11-11-replace-content-merge-integrity, 2026-11-08-subagent-patch-field-drift-silent-content-loss, 2026-11-11-subagent-wiki-patch-code-refs-read-verify, 2026-11-13-inline-line-refs-force-replace-content]
---

# 合并脚本 code_refs 替换语义下子集 patch 丢锚：合并前与索引基线做并集保护

## Scenario

Wiki 增量更新流水线的 patch 合并环节：编排者并行派 6 个只读修订 subagent 产出小节级 patch JSON（`section_title`/`action`/`new_content`/`code_refs`），随后逐个交给 `merge_section_patch.py` 合并进 Wiki 文档。规模：6 个 patch / 13 个小节 / 原索引约 262 个 code_refs 锚点。小节多为 line_number_only（仅刷行号），少数 replace_content（正文修订）。

## Key Signals

- 多个 subagent 返回的 code_refs 是 wiki-index 原小节引用的**子集**而非全集：P003 主文档架构设计 6 锚只回 3、知识库笔记概述原 14 条只回 3，business_term 两个小节干脆全回 `[]`——subagent 天然只回"本次核对过"的条目。
- 读 `merge_patch` 源码确认消费端语义：`p.get("code_refs", [])` 逐条计算 hash 进 `hashes_updated`，patch 集合之外的原引用不再参与后续索引重建——**整体替换语义坐实，空列表同样清空原引用**。
- patch 同时夹带两类脏数据：4 条引用丢目录前缀（`tools/prepare.py` 少了 `workspace/02_软件源码/workflow_base/` 层级）、1 条无行号条目（imports.json）在原索引中根本不存在此锚。

## Essence

替换语义的合并脚本对 code_refs 的处理是"patch 给什么就用什么"，而 subagent 的返回倾向是**子集**（与既有经验管制的**越界扩充**方向正好相反）：直接合并时原锚点静默丢失，随 build_index 固化后下游检索引用断链，且丢锚无任何报错信号。防丢失的唯一时机在合并之前——把每个 patch 小节的 code_refs 与索引基线做**并集保护**，让"基线锚点"成为合并结果的下界。

## Approach

1. **先读消费端脚本源码确认语义**：code_refs 是替换还是合并只能从 `merge_patch` 实现确认，patch JSON 结构本身携带不出该信息；替换语义即触发本模式。
2. **合并前并集保护预处理**：对每个 patch 小节，code_refs 与 wiki-index 该小节原引用做并集——新集合条目全进；**同名文件以新行号集合整体替换**（不是逐条并集，防旧 `:55` 与新 `:57` 并集后留脏锚）；原独有文件（基线有、patch 没有）原样保留。
3. **伴随两项修正**：patch 中短路径（丢前缀）按后缀匹配映射回全路径；无行号且原索引无此锚的条目剔除（防索引 format_errors）。
4. **合并后锚点级验证**：跑 build_index 后核对锚点数与抽查快照——原锚点全部保留 + 新锚点补建成功即为通过；锚点数净减须能归因（如无行号锚剔除）而非静默丢失。

## Faster Next Time

- 判定口诀成对记忆：**回退堵多余**（subagent 越界扩充 → 裁剪回基线，见 2026-11-09 条）、**并集堵丢失**（subagent 子集返回 → 合并前补齐基线，本条）——两者是同一校验主题的两个互补面，缺一即另一方向的静默污染。
- 收到 patch 的第一动作：比对每个小节 patch code_refs 条数与基线条数，patch ⊂ 基线即触发并集保护；全空 `[]` 是最高危信号。
- ROI：一轮预处理（读索引 + 集合运算）约数分钟，避免的是锚点静默丢失后下游检索断链、重建索引返工的整链成本；且预处理产物可直接留痕供校验追溯。
- 反模式：假定合并脚本会"智能合并"引用集；只校验 patch 自身合法性（字段名/引号形态）不校验引用集与基线的集合关系；把子集返回当"subagent 精简了引用"而放行。

## Applicability Boundaries

- 适用：消费端为替换语义合并脚本、权威锚点集在索引基线（wiki-index 等）中的结构化 patch 流水线；LLM 产出 + 脚本消费的任何"引用集/锚点集"合并链路。
- 不适用：合并脚本本身已是并集语义（此时子集返回无害，但仍建议核对行号新鲜度）；subagent 越界扩充场景（归 2026-11-09-subagent-patch-code-refs-baseline-fallback 管制）；索引基线缺失或已过期的场景（须先重建基线再校验）。
- 与相邻经验分工：本条管"引用集合并前的集合关系防护"，replace-content-merge-integrity 管"replace_content 正文的原文保全与计数断言"，field-drift 条管字段名/字符形态漂移，code-refs-read-verify 条管 patch 引用的实读核实——四者在 patch 流水线的不同失效面互补。

## Evidence or Examples

- 源会话 ses_e2d0191d6ffejSEq6m0pmTb0hf（docgen-apply fork #1，Date 项目 Wiki 增量更新，6 变更文件触发 6 篇文档修订）。
- 子集实证：6 个 patch 中 3 个为明显子集（P003 架构设计 6→3、知识库笔记 14→3、business_term 全空），若直接合并将丢失 20+ 条原锚点。
- 修正实证：4 条丢前缀路径（如 `tools/prepare.py:71` → `workspace/02_软件源码/workflow_base/tools/prepare.py:71`）映射回全路径；imports.json 无行号锚剔除后索引 format_errors 为空。
- 验证实证：并集保护后 6 个 merge 全部 rc=0；build_index 增量统计 reused 9 / updated 6 / added 0、code_paths_verified 254；P003 文档索引快照确认 `adapter/capture.py:31` 补建成功且原锚点 `adapter/whitelist.py:28` 保留——并集与补建双向生效。