---
id: 2026-11-08-ghost-reference-path-precheck
title: 任务清单生成前对上游引用路径做幽灵引用预检，不存在项按上游口径分"待新建"与"幽灵引用"两类
category: workflow
nature: technique
created_at: 2026-11-08T02:26:32
updated_at: 2026-11-08T02:26:32
tags: [任务清单, 路径预检, 幽灵引用, SDD, 前置检查]
keywords: [幽灵引用, 路径预检, glob 验证, 任务清单生成, 待新建判定, 引用完整性, 下游执行代理, 防执行期返工, 存在性核验, SDD tasks 阶段]
problem_patterns:
  - 生成任务清单/规划产物时直接照抄上游文档中的文件路径引用而未验证存在性，下游执行代理跑到该任务才爆雷返工
  - 预检发现某路径不存在时一刀切处理：要么当错误报、要么静默跳过，误伤上游声明"待新建"的正常缺失，或漏掉真正的幽灵引用
source_sessions: [ses_e48cee654ffec1l2Z993I0f4iF]
project: Date
severity: medium
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [workflow/2026-11-07-sdd-spec-to-tasks-coverage-mapping, agent-ops/2026-11-07-refresh-env-baseline-before-planning, agent-ops/2026-11-07-write-receipt-not-proof-of-persistence, workflow/2026-11-08-task-list-alignment-revision-terminal-state-annotation]
---

# 任务清单生成前对上游引用路径做幽灵引用预检，不存在项按上游口径分"待新建"与"幽灵引用"两类

## Scenario

SDD 流水线的 tasks 阶段：spec/design 已定稿（数百行，内含大量文件路径引用——子智能体配置、技能 SKILL.md、MCP 配置、规则文件、机制文档、档案区），任务清单要把这些路径落进任务"涉及文件"字段，交付给下一个执行主体消费。此时上游文档里可能混着两类路径：真实存在的存量路径，以及"计划中即将新建"的尚不存在路径。本次触发场景：为 8 任务组 34 任务的 tasks.md 动笔前，先对设计文档引用的全部路径做存在性预检，其中确有一个技能路径不存在。

## Key Signals

- 产物角色信号：任务清单的消费者是另一个执行代理，不是当前会话自己——路径错误要到执行期才暴露，返工成本最高。
- 引用密度信号：上游文档内嵌十几处路径引用（agents/、skills/*/SKILL.md、mcp_settings.json、rule/*.mdc、notes/、档案区/），逐条手工核对不可靠，需要结构性手段。
- 混合状态信号：上游口径中明确存在"待新建"产物（如新技能）——"路径不存在"因此不是单值结论，不能一律当错误。

## Essence

任务清单里的路径引用是下游执行代理的输入契约，幽灵引用（引用了不存在且上游也以为存在的路径）在执行期才爆雷、返工成本最高，所以预检必须前移到生成时（写文档前）而非评审时。预检的核心不是"查存在性"这个动作，而是**不存在项的口径回查**：回上游文档对照，"上游声明待新建"的缺失是正常状态（任务里如实标注待新建即可），"上游假设已存在"的缺失才是幽灵引用（须回溯上游修正或改写任务）。不区分两类，预检要么产生误报噪音、要么漏掉真问题。

## Approach

1. **目标产物重名检查**：glob/列目录确认目标文件（如 tasks.md）不存在，冲突则换名，绝不覆盖。
2. **引用路径全量提取与逐条验证**：从上游 spec/design 提取全部路径引用清单，逐路径 glob 验证；相互独立的验证可并行发多个 glob 一轮完成。
3. **不存在项回查上游口径分类**：对每个 glob 空结果，回上游文档查口径——
   - 上游声明"待新建/规划中产物" → 判为符合预期，在任务中如实标注"待新建"；
   - 上游假设已存在 → 判为幽灵引用，回溯上游修正口径或改写任务，禁照抄落盘。
4. **预检结论写进生成摘要**：向用户呈报时附一句预检结果（如"全部路径已核实，X 项符合待新建预期"），让确认动作有据可查。

## Faster Next Time

- 动笔三问自检：目标产物重名查了吗？上游引用路径逐条 glob 了吗？不存在项按口径分类了吗？——三问全过再写文档。
- 警告信号：任务清单里要写"新建 XX 文件"类任务时，同时写明"该路径当前不存在为预期状态"，给下游免歧义。
- ROI：本次预检开销约 4 个并行 glob（一轮完成），34 任务的路径引用零幽灵、下游执行零路径性返工；若漏检，最坏情形是执行代理在门禁任务上因路径缺失中断回炉。
- 反模式：只查目标产物重名、不查引用路径（覆盖了既有经验的一步却漏了本条主体）；把所有不存在项当错误上报（误报噪音淹没真问题）；预检结果不落摘要（用户确认时无据可核）。

## Applicability Boundaries

- 适用：生成将被另一个执行主体（子代理/下一阶段/后续会话）消费的规划产物，且产物内引用具体文件路径；上游文档引用密度越高收益越大。
- 不适用：纯描述性产物（无路径引用）；单会话内自己即时执行且路径错误可即时发现的场景（预检是纯开销）；上游路径引用仅为示例性、非执行对象的文档。
- 相邻经验划界：`agent-ops/2026-11-07-refresh-env-baseline-before-planning` 管环境基线漂移（已完成项标待验收），本条管产物内引用路径的存在性；`workflow/2026-11-07-sdd-spec-to-tasks-coverage-mapping` 的"先查产物重名"是本条第 1 步的子集，本条把预检扩展到引用路径全量；`agent-ops/2026-11-07-write-receipt-not-proof-of-persistence` 管写后验证，本条管写前预检，一前一后互补。

## Evidence or Examples

- 本次实战（源会话 ses_e48cee654ffec1l2Z993I0f4iF，spec-task-agent fork #1）：生成 tasks.md（8 任务组 34 任务）前，先 glob 确认 tasks.md 不存在，随后两轮并行 glob 验证设计文档引用路径——agents/examiner.md、agents/grader.md、13 个技能 SKILL.md、mcp/mcp_settings.json、rule/项目协作公约.mdc、notes/ 机制文档、notes/档案区/ 全部在位。
- 关键判定实例：技能 sdd-ref-distill 路径 glob 为空 → 对照设计口径"待新建（C1 能力迁移产物）" → 判为符合预期而非报错，预检结论"全部核实、sdd-ref-distill 不存在符合待新建预期"写入生成摘要。
- 诚实标注：34 任务路径零幽灵引用为实测；"防执行期返工"的 ROI 为推断（本轮无对照事故，依据是下游消费结构与路径依赖的链路分析）。