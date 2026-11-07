---
id: 2026-11-07-gate-exemption-semantic-annotation
title: 能力有边界的自动化门禁：豁免须语义化标注而非静默跳过
category: workflow
nature: decision
created_at: 2026-11-07T08:51:58
updated_at: 2026-11-07T08:58:16
tags: [quality-gate, exemption, semantic-annotation, false-pass-prevention, capability-boundary]
keywords: [门禁豁免, 审查能力边界, 语言特定检查, P3C, 虚假通过, 留痕, 编码必审, 受控旁路]
problem_patterns: [门禁工具对当前变更类型不适用, 为赶流程静默跳过检查]
source_sessions: [ses_e4c8a78edffee772ytCDqwOSfb]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["2026-11-07-deliberate-violation-sample-smoke-verification", "2026-11-07-full-authorization-self-gated-execution", "2026-11-06-project-knowledge-provenance-format"]
---

# 能力有边界的自动化门禁：豁免须语义化标注而非静默跳过

## Scenario

提交/完工门禁中包含语言特定的检查（如 P3C 静态规约审查，适用边界=仅 Java），而当前批次变更全部为 Markdown/JSON/PowerShell——检查工具对本批变更**根本不适用**。门禁要求"未过不完工"，此时如何处置豁免。

## Key Signals

- 触发信号：门禁条款生效，但检查能力的适用边界与变更类型不相交。
- 危险信号：为了走完流程而静默跳过（留痕断链），或伪造"通过"记录（门禁退化成橡皮图章）——后者危害更大，因为它污染了门禁的全部历史可信度。

## Essence

豁免是**受控旁路**，与违规有本质区别：

- 静默跳过 = 检查发生与否不可审计；
- 伪造通过 = 门禁语义被破坏；
- **语义化豁免 = 显式声明"检查未发生+为何不适用+依据出处"**，让审计者能独立复核豁免的合法性。

判定规则：能力适用边界是门禁设计时写明的属性；变更落在边界外时，豁免自动成立，但成立本身必须留痕，且标注内容须可判定（禁"不适用"三个字糊弄过去）。

## Approach

1. 门禁设计阶段：在每条能力型检查上写明适用边界（语言/文件类型/平台），并预置"豁免语义标注行"字段。
2. 执行阶段命中边界外变更时，输出标注行，至少含：变更类型清单、不适用理由、依据出处（注册表条目/文档位置）。
3. 标注行随留痕文档落盘，与"通过"记录同等地位存档；门禁结论记为"豁免通过（语义标注 N 行）"而非裸"通过"。
4. 批内一旦出现边界内文件（如任何 `.java`），立即取消豁免走实审，未过不完工。
5. 区分两种情形：能力**不适用**（边界外）→ 自主语义豁免；能力**应适用但未就绪**（如审查引擎没构建好）→ 禁自判豁免，须呈报"能力未就绪"并请求用户明示豁免授权。

## Faster Next Time

- 检查单模板预置豁免标注字段，执行时按字段填空，避免临场编造措辞。
- 把"豁免标注行"纳入提交门禁的清单核对项：有豁免行 → 核对变更类型确实全部在边界外。
- 自查口诀：**"豁免可自判（边界外），未就绪须呈报（边界内未跑）"**——两类情形混淆即违规。

## Applicability Boundaries

- 适用：能力有明确适用边界的自动化门禁（语言特定审查、平台特定扫描、架构特定检查）；任何要求"未过不完工"的纪律场景。
- 不适用：能力可用且在边界内但结果未出——这须等待或呈报，不存在豁免；人工评审类门禁（豁免权天然在评审者，无此问题）。
- 前提：适用边界在设计时已明确写明；边界模糊时先补边界定义再谈豁免，禁临场解释边界。

## Evidence or Examples

- 实例（2026-11-07，kb_arch_foundation 组 12）：65 文件提交批次全部为 Markdown/JSON/PowerShell，G4（P3C 审查）按边界豁免；脚本自测输出 `no-java-changes: skip review` 作为豁免依据留痕；同会话多次出现"变更类型=Markdown/JSON 配置+PowerShell 只读核验命令，非 Java，P3C 不适用（语言边界=仅 Java），豁免留痕"的标准化标注行。
- 反面对照（同会话设计约束）：P3C 未就绪场景的处理路径被显式定义为"呈报未就绪+用户明示豁免方可提交，禁虚假通过"——即第 5 步规则的出处，两类情形在设计文档中即已分流。