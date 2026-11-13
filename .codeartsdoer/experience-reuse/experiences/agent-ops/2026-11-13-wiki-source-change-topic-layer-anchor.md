---
id: 2026-11-13-wiki-source-change-topic-layer-anchor
title: 源码实现细节变更 × 主题 Wiki 文档的层面锚点判定——主题层面未动即降级 line_number_only + code_refs 双形态填法
category: agent-ops
nature: methodology
created_at: 2026-11-13T12:03:10
updated_at: 2026-11-13T12:03:10
tags: [wiki修订, 层面锚点, line_number_only, 主题文档, 源码变更]
keywords: [依赖管理, import面, code_refs 空数组, 实现细节更新, patch JSON, 节级分流, 降级判定, 只读 subagent, S2影响级别, 层面无关]
problem_patterns:
  - 源码文件实现细节更新（状态机/常量值/映射表）被列入主题 wiki 文档修订派工，误判为需重写正文会把实现细节噪音注入依赖管理等主题层小节
  - line_number_only 型 patch 的 code_refs 字段不知如何填：无引用关系的小节误补文件级引用或误置 null/省略字段
source_sessions: [ses_e2d0d6687ffeuNJrB4ZATrjxTB]
project: Date
severity: low
quality_score: 84
hit_count: 1
last_hit_at: 2026-11-13T13:02:13
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-08-wiki-section-tiered-revision-judgment-contract, 2026-11-08-wiki-section-revision-patch-json-mode, 2026-11-11-patch-new-content-section-title-stripping]
---

# 源码实现细节变更 × 主题 Wiki 文档的层面锚点判定——主题层面未动即降级 line_number_only + code_refs 双形态填法

## Scenario

以只读 subagent 身份接收主题型 project-knowledge wiki 文档（本例"依赖管理"主题）的节级修订派工，影响级别 S2。变更源是单个源码文件（本例 `adapter/receipt.py`：FRAMEWORK_READY 常量、ACTION_FRAMEWORK 映射、DrillEngine 状态机的实现更新），派工单受影响小节两节（关键文件与位置 / 架构与约定）并给出预判 action。任务边界：逐节判定 action 并输出结构化 patch JSON，禁止写文件。

## Key Signals

- 派工单声明变更性质："仅标准库 + 内部模块互引，无任何 import/依赖声明变化"，并给出反条件门："仅当你核实实际新增/移除了 import 才允许 replace_content"——预判附带了升级条件。
- 变更实文本身（就绪状态字典、动作→框架映射、回合状态机）全部落在实现细节层，不在依赖声明、import 面、分层结构任何一个依赖管理主题的承载层面。
- 受影响小节的 code_refs 分布不对称：一节有 6 条引用但均与变更文件无引用关系且行号未变；另一节正文叙述性、本无 code_refs。
- 派工单提供符号骨架路径与关键行号（DrillEngine 类在 37 行）作为核对锚点。

## Essence

**变更文件被波及 ≠ 主题层面被动**。主题 wiki 文档的"同层面"判定要落到**主题维度的层面锚点**上：依赖管理主题锚定"依赖声明（pyproject/composer 等）+ import 面"，状态机逻辑、常量取值、映射表更新等实现细节不落在该层面 → 即使变更文件为 modified 且影响级别 S2，主题小节仍层面无关 → 全部降级 `line_number_only`（正文 new_content=null）。执行上还有两个不易自查的点：（1）派工单"无 import 变化"是声明不是证据，import 面必须实读源码 import 区核实；（2）`line_number_only` 的 `code_refs` 双形态——小节原有引用且全部未变更 → **原样保留全量列表**（行号不动）；小节本无引用 → **空数组 `[]`**，不置 null、不省略字段、不画蛇添足补文件级引用。

## Approach

1. **实读核实 import 面**：读变更源码的 import 区（本例行 8-22），逐条核对是否只有标准库与内部模块互引——派工单说"无 import 变化"只当作待验证假设。
2. **确认变更文件状态**：git status 核实文件确为变更态（本例 `?? adapter/receipt.py`），避免对未变更文件空转判定。
3. **对照符号骨架核对行号锚点**：用派工单给的符号骨架确认变更文件关键符号行号（本例 DrillEngine 类 = 37 行），保证任何引用更新有行级依据。
4. **逐节套主题层面锚点**：对每个受影响小节问"小节正文是否承载了变化的层面口径？"（依赖管理 → 问 import/依赖声明/分层结构）；否 → `line_number_only`，`new_content: null`。
5. **code_refs 双形态填法**：小节原有引用且未变更 → 原样保留全量列表；小节本无引用 → `"code_refs": []`；仅在确有行级依据时增删引用。
6. **patch JSON 严格直出**：以 `{` 开头、无 markdown 包裹，`section_title` 逐字复制 `##` 后标题，交上游合并脚本应用。

## Faster Next Time

- ROI：两小节零重写、仅维护 patch 结构与引用核对，避免把状态机实现细节写进依赖管理文档的噪音返工；判定时间压缩为一次 import 区实读 + 一次骨架对照。
- 判定口诀：先定主题层面锚点（依赖管理 = 声明 + import 面），锚点未动 → `line_number_only`；`code_refs` 有则原样保留、无则 `[]`。
- 警惕信号：派工单写"无 import/依赖变化"→ 仍须实读 import 区（声明非证据）；看到小节在受影响清单里就想 `replace_content` → 先问层面锚点；想给无引用小节补文件级 `:1` 应付 → 空数组才是合法形态。

## Applicability Boundaries

- 适用：源码变更波及**主题型** wiki 文档（依赖管理/构建配置/环境资产等以"声明面"定义关注点的主题）的节级修订判定；`line_number_only` patch 中 `code_refs` 字段的输出形态选择。
- 不适用：import 面真实增减或依赖声明文件（pyproject/composer/requirements 类）变更 → 主题层面被动，必须 `replace_content` 重述；文档口径变化波及枚举型小节的通用同层面分流 → 走 tiered-revision-judgment-contract；建议-合并分离与 patch 落盘契约 → 见 wiki-section-revision-patch-json-mode。
- 与相邻经验分工：`2026-11-08-wiki-section-tiered-revision-judgment-contract` 管同层面分流的通用判据（其场景是文档条目口径变化），本条把判据实例化到"源码变更 × 主题文档"并补充主题层面锚点概念与 code_refs 双形态输出细节；`2026-11-08-wiki-section-revision-patch-json-mode` 管 patch 载体与合并分离；`2026-11-11-patch-new-content-section-title-stripping` 管合并前的 new_content 标题行剥离校验。
- 证据等级：单次实战闭环（import 区实读 + 双形态 patch 输出一次合规）；层面锚点概念目前仅在"依赖管理"主题验证，其他主题（安全、性能等）的锚点定义待复用时归纳。

## Evidence or Examples

- 源会话 ses_e2d0d6687ffeuNJrB4ZATrjxTB（@general 修订 subagent，trace 内联提供）。
- import 面实读证据：`adapter/receipt.py` 行 8-22 仅有 `from __future__ import annotations` + 标准库（typing 等）+ adapter 内部互引（storage/boundary/errors/models/whitelist），零第三方 import。
- patch 输出证据：`关键文件与位置` → line_number_only，6 条 code_refs 原样保留（pyproject.toml:6、workflow_base cli.py:10-14、composer.json:8、Parsedown.php:5-9、recaptchalib.php:3、imports.json）；`架构与约定` → line_number_only，`"code_refs": []`。
- 符号骨架证据：`.codeartsdoer/.codebase/branches/master/docs/skeleton/adapter.txt` 确认 DrillEngine 类在 37 行，与派工单声明一致。