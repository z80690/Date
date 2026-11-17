---
id: 2026-11-13-inline-line-refs-force-replace-content
title: Wiki 小节正文内嵌行号引用的 action 升级判据：口径零漂移但行号文字位移须 replace_content 局部刷新
category: workflow
nature: decision
created_at: 2026-11-13T11:53:14
updated_at: 2026-11-13T11:57:27
tags: [文档修订, patch决策, 行号引用, 零漂移, code_refs]
keywords: [line_number_only, replace_content, 正文内嵌行号, 文件:行号引用, 零漂移, 守卫函数, 抛点位移, code_refs 补锚点, 逐节分流, patch JSON]
problem_patterns:
  - 源码重构（守卫函数抽取/统一入口化）后异常语义未变仅抛点行号位移，误判"口径未变 → 全线 line_number_only"，导致小节正文内嵌的 `文件:行号` 区间引用文字残留旧值
  - 重构把内联抛点抽成守卫函数后抛点一分为二（守卫函数体内 + 入口兜底），code_refs 未按新抛点结构补锚点，文档引用覆盖不全
source_sessions: [ses_e2d0d0ea0ffeUEzeC14VGPFT9M]
project: Date
severity: low
quality_score: 86
hit_count: 1
last_hit_at: 2026-11-15T20:03:04
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-wiki-section-same-layer-action-criteria, 2026-11-11-wiki-verbatim-consistency-line-number-only, 2026-11-08-wiki-section-tiered-revision-judgment-contract, 2026-11-09-subagent-patch-code-refs-baseline-fallback, 2026-11-13-merge-code-refs-replace-semantics-union-guard]
---

# Wiki 小节正文内嵌行号引用的 action 升级判据：口径零漂移但行号文字位移须 replace_content 局部刷新

## Scenario

只读 subagent 承接项目规范知识（wiki）小节级增量修订派工，以 patch JSON 交付（action ∈ replace_content / line_number_only），禁止直写文件。变更源是 Python 源码重构：抓包会话管理统一为 `capture_session(op=start/stop/health_check)` 单一入口，内联工具校验抽成 `_assert_tool` 守卫函数。异常处理约定与转译链语义完全未变（错误码数量不变、异常类型→错误码映射不变），仅抛点行号位移。影响级别 S2。此类"语义零漂移 + 行号位移"的修订在高频派工中反复出现，action 误判直接造成合并后正文残留旧行号。

## Key Signals

- 易误判信号："异常语义零漂移"（错误码、转译映射未变）直觉上指向全线 line_number_only——与"零漂移 → 全线 line_number_only"既有经验呼应。
- 决定性信号：其中一个小节的正文文字**内嵌**了 `文件:行号区间` 引用（如转译链举例 `capture.py:55-58`），该行号已位移——line_number_only（new_content=null）只刷新 code_refs 列表，永远触不到正文文字。
- 重构形态信号：守卫函数抽取使抛点一分为二——守卫函数定义处（:23-28）+ 入口 unknown-op 兜底抛出（:45），旧文档的单锚点不再覆盖新抛点结构。

## Essence

"口径零漂移"只豁免**内容重写**，不豁免**行号文字修正**：正文内嵌的 `文件:行号` 引用文字也是正文的一部分，其准确性属于行号维护职责，只能由 replace_content 承载。因此零漂移场景的 action 决策要在"逐字比对一致"之后追加一步——检查正文是否内嵌受影响文件的行号引用文字：有 → replace_content（正文仅改行号，其余句子逐字保留）；无 → line_number_only。同一轮派工内两节分流并行出现（一节 line_number_only + 一节 replace_content）是常态而非异常，按节判定而非按轮统一。

## Approach

1. 实读变更源文件全文与符号骨架，确认重构后抛点结构：守卫函数定义行、入口兜底抛出行、转译 except 块行区间。
2. 逐节检查正文是否内嵌受影响文件的 `文件:行号`（或行号区间）引用文字——grep 正文 `\.py:\d` 类模式辅助定位；命中且行号已位移 → 该节 replace_content，new_content 只改行号区间、其余句子逐字复制。
3. 正文不含该文件行号文字 → line_number_only，new_content 严格为 JSON null（非 "null" 字符串），仅刷新 code_refs。
4. code_refs 按新抛点结构补锚点：守卫函数定义行 + 入口兜底抛出行 + 转译块起始行，全部以本次实读为依据（与符号骨架锚点交叉核对），不沿用旧文档值。
5. 每节决策留一句理由（如"正文含 capture.py:55-58 内嵌引用，须 replace 同步行号"），供上游合并方复核。

## Faster Next Time

- ROI：一步 grep（正文内嵌行号模式）即可把零漂移场景的 action 决策从直觉判断变为机械检查，避免合并后正文残留旧行号的二轮返工。
- 快捷判据：`grep -n "\.py:[0-9]" 小节正文` 命中受影响文件 → replace 候选；未命中 → line_number_only。
- 反模式：见"语义未变"就全线 line_number_only（正文内嵌行号文字漏改）；为刷行号而重写整段正文（引入无关漂移，违背逐字保留原则）。

## Applicability Boundaries

- 适用：patch JSON 小节级修订派工中，变更源为源码重构（抛点位移/守卫函数抽取/入口统一化）且异常语义零漂移的场景；任何正文内嵌 `文件:行号` 引用文字的 wiki 小节维护。
- 不适用：口径实质变更（须整节重写，行号刷新只是附带）；纯文档源（无代码行号可嵌，行号锚点映射见 tiered-revision-judgment-contract）；全新文档生成（无既有小节可比）。
- 与相邻经验分工：`wiki-verbatim-consistency-line-number-only` 管口径型零漂移的"全线回落 line_number_only"（其正文无内嵌行号文字的前提成立时）；本条补其反例分支——零漂移但正文内嵌行号文字位移时须混合 action。`wiki-section-same-layer-action-criteria` 管内容口径层面的同层面分流；本条管行号维护层面的二次分流，是其细化。`wiki-section-tiered-revision-judgment-contract` 管 code_refs 保守原则（新增引用须有行级依据）；本条的守卫函数双锚点补列是该原则在重构场景的实例。`subagent-patch-code-refs-baseline-fallback` 管扩充引用的实读取证；本条的重构补锚点同样以实读为前提。
- 证据等级：单次实战闭环（两节分流决策 + patch JSON 输出结构合规），无失败对照；判据源自派工单规则的首轮实战验证与操作化细化，跨文档复用稳定性待同类任务检验。

## Evidence or Examples

- 源会话 ses_e2d0d0ea0ffeUEzeC14VGPFT9M（@general 修订 subagent，trace 内联提供；Date 项目 error_handling wiki 修订派工）。
- 分流实证：小节"关键文件与位置"正文无 capture.py 行号文字 → line_number_only（new_content=null），code_refs 在基线之上补 `adapter/capture.py:23`（_assert_tool）与 `adapter/capture.py:45`（unknown op 兜底 E_IFACE_UNAVAILABLE）；小节"架构与约定"正文内嵌 `capture.py:55-58` → replace_content，正文仅将该区间刷为实读后的新行号（57-60），其余约定文字逐字保留。
- 实读链路：wiki 文档全文 + adapter/capture.py 实读（_assert_tool 在 23-28、capture_session 入口 31、E_IFACE_UNAVAILABLE 兜底 45）+ adapter 符号骨架交叉核对（_assert_tool 23、capture_session 31、_start 48）。
- 派工单内嵌判定规则佐证："line_number_only……除非你核实正文小节内嵌的 `文件:行号` 引用文字需要更新"——本次为该规则的首轮实战执行与 grep 操作化。