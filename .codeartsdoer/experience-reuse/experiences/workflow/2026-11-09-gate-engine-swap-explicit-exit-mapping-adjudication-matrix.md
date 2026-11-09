---
id: 2026-11-09-gate-engine-swap-explicit-exit-mapping-adjudication-matrix
title: 审查门禁引擎替换：exit 语义显式映射替代透传 + 裁决矩阵唯一裁决 + 非零即拦截 fail-closed
category: workflow
nature: decision
created_at: 2026-11-09T01:32:45
updated_at: 2026-11-09T01:32:45
tags: [审查门禁, 工具替换, exit 映射, fail-closed, 裁决矩阵]
keywords: [门禁脚本, exit 语义, 透传失效, 显式映射, 裁决矩阵, fail-closed, 非零即拦截, exit-zero 禁用, 双向隔离, 等价演练, 引擎替换]
problem_patterns: ["旧门禁脚本的 exit 语义靠'引擎退出码恰好等于门禁语义'的透传机制，更换引擎后退出码含义完全不同，沿用旧骨架导致门禁误放行或误拦截", "新引擎的异常退出码与文档/直觉不符（如文件级异常走违规码而非进程异常码），按具体退出码逐码枚举映射出现漏网语义", "替换审查工具时旧门禁脚本保留原样，新旧技能并存期间误触发旧工具或新旧互相引用造成双门禁混乱"]
source_sessions: [ses_e43dfeddbffecZ9Y91Am1PbKju]
project: Date
severity: high
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [workflow/2026-11-07-gate-exemption-semantic-annotation, workflow/2026-11-09-constraint-tool-decoupling-zero-rule-touch, testing/2026-11-07-deliberate-violation-sample-smoke-verification]
---

# 审查门禁引擎替换：exit 语义显式映射替代透传 + 裁决矩阵唯一裁决 + 非零即拦截 fail-closed

## Scenario

审查门禁（"编码必审未过不完工"的执行载体）需要从引擎 A（PMD/P3C）替换为引擎 B（Ruff），旧门禁脚本的 exit 语义与门禁语义靠"引擎退出码恰好同值"隐性衔接；且用户要求旧文件零删除、新旧技能过渡期并存。

## Key Signals

- 读旧脚本发现 exit 为**透传机制**：引擎退出码原样作为门禁退出码返回，无映射层——旧引擎（PMD）的 0/4 恰好与门禁两值域同构才"看起来能用"。
- 新引擎实测退出码与直觉不符：文件级异常（E902）走 exit 1，而非按"进程级异常"预期的 2——按码枚举的映射会漏。
- 替换若只改调用行沿用旧骨架，异常路径（git 不可用、报告不可写）无显式裁决，fail-open 风险隐藏在从未跑过的分支里。

## Essence

1. **透传是隐式契约**，换引擎即失效。替换的第一动作是建立**显式映射层**：把"引擎现象 → 门禁语义"的全部场景枚举成裁决矩阵（无违规/有违规/文件异常/进程异常/前置工具不可用/报告不可写/空集豁免/显式列表），作为唯一裁决依据，而非逐码翻译。
2. **fail-closed 写成"非零即拦截"而非按码枚举**：引擎退出码语义会随版本与场景漂移，"0=放行，其余一律收敛到拦截码 + verdict 标注 + 异常原文入报告"对参数面变化鲁棒。
3. **门禁弱化参数是替换期的隐形退化面**：`--exit-zero`（违规返 0）、`--watch`（轮询）、`--fix`（审改合一）类参数一律禁用，写进脚本约束并 grep 复核。
4. **过渡期新旧并存靠双向隔离**：旧承载零删除仅解绑（语义），双向 grep 核验互不引用；触发源（落盘/提交前/流程门禁）与门禁入口解耦，用显式列表样例做等价演练验证同一入口。

## Approach

1. 读旧脚本定性 exit 机制：若为透传，列为关键结构改动；梳理门禁全场景集，一格一场景。
2. 实测新引擎退出码：干净、违规、文件级异常（传不存在路径）三类各跑一次，用实测值定矩阵，不信文档假设。
3. 实现五段处理流：报告可写预检（留痕先行，不可写直接拦截）→ 文件集确定（git 变更集或显式列表，git 不可用 fail-closed）→ 空集短路（豁免语义如实标注留痕，不调用引擎）→ 引擎调用（输出原文整体入报告，禁删减）→ 矩阵裁决落盘后以门禁码退出。
4. 裁决收敛规则：引擎 exit 0 → 门禁 0；一切非零 → 拦截码 + verdict 标注（violations-found/file-error/unexpected-error 分型）+ 异常原文入报告；前置失败（工具不可用/报告不可写）直接拦截，禁任何完工结论。
5. 禁用项写进脚本注释区并 grep 复核零调用；新旧技能做双向 grep 互不引用核验。
6. 等价演练 + 两面证据：显式列表样例验证同一入口；触发演练须覆盖"有产物必审通过才放行"与"无产物如实标注豁免"两面，缺面补跑加强版。

## Faster Next Time

- 口诀："换引擎先问 exit 谁定义——透传即重写，映射按矩阵，非零即拦截"。
- 验收清单：矩阵逐格实测、禁用参数 grep 零命中、双向隔离零引用、两面演练证据、引擎原文入报告禁删减。
- 预警信号：新引擎某退出码"只出现一次再没见过"，按非零即拦截兜底，而不是补枚举。

## Applicability Boundaries

- 适用：门禁/CI 工具替换、linter 引擎迁移、任何"以外部进程退出码做放行判定"的脚本改造。
- 不适用：门禁码与引擎码本就显式分离的既有设计（只需引擎适配层）；非退出码驱动的判定机制（如解析报告文本做判定）。
- 边界：矩阵以实测为准，引擎升级后须重测受影响格；本模式不定义触发时机（落盘/提交/流程门禁由项目事件通道决定）。

## Evidence or Examples

- 来源会话：ses_e43dfeddbffecZ9Y91Am1PbKju（2026-11-09，Date 项目 20261109_ruff_review_gate 特性执行阶段，P3C/PMD → Ruff 0.17.2）。
- 实测：旧 review-code.ps1 为透传机制（PMD 码恰为 0/4）；Ruff 干净 exit=0、违规（F401）exit=1、文件级异常（E902）exit=1 非 2——据此把预设"异常按码 2 映射"改判为"非零即 4"。
- 验证：裁决矩阵 D1~D8 九场景实测全符合；T1~T5 五类用例 5/5 PASS；提交前演练实测 exit 4 拦截 git commit、修复后 exit 0 放行；性能红线端到端 0.52s/60s、引擎 0.06s/10s。
- 与 workflow/2026-11-07-gate-exemption-semantic-annotation 的分工：那条管门禁能力边界外的豁免须语义化标注（不适用场景如何放行）；本条管引擎替换时门禁语义本身的显式映射与 fail-closed 收敛（工具换了语义怎么保真）。
- 与 workflow/2026-11-09-constraint-tool-decoupling-zero-rule-touch 的分工：那条管替换前"规则层要不要动"的原文实查判定；本条承接其结论，管"技能/脚本层的引擎替换怎么实现语义等价"。