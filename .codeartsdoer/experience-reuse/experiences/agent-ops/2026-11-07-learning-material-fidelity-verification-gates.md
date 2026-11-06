---
id: 2026-11-07-learning-material-fidelity-verification-gates
title: 外部材料清单纳入前的保真度四门验证：存在性→相关性→时间窗→质量门槛，淘汰与降级必须留痕
category: agent-ops
nature: methodology
created_at: 2026-11-07T04:37:00
updated_at: 2026-11-07T04:54:36
tags: [material-vetting, anti-fabrication, verification-gates, citation-fidelity, learning-materials]
keywords: [保真度验证, 材料清单, arXiv 实证, GitHub API, 编造拦截, 时间窗核对, 淘汰留痕, 超窗候选, 存在性验证, 质量门槛, ID 张冠李戴, 引证失真]
problem_patterns: [候选论文/项目凭检索或记忆列入清单未经官方源逐条核实, 材料 ID 与真实内容张冠李戴造成引证失真, 真实但超出时间窗或质量门槛的材料如何处置]
source_sessions: [ses_e4f5c5a83ffefUFnzHFvOEFJCW]
project: Date
severity: high
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-verify-claimed-prerequisites-before-research, 2026-11-06-multi-purpose-resource-threshold-separation, 2026-11-06-learning-artifact-five-element-sedimentation, agent-ops/2026-11-07-worker-grader-exam-gate-pattern]
---

# 外部材料清单纳入前的保真度四门验证：存在性→相关性→时间窗→质量门槛，淘汰与降级必须留痕

## Scenario

考核/学习类任务要求纳入固定数量的外部材料（论文、开源项目），用户对材料设硬门槛（"保真度必须准""近 1 年内""大厂高引用框架、禁 hello world 类"）。候选材料来自检索结果或记忆，若不验证直接列入清单，会出现 ID 张冠李戴、超窗混入、以工具冒充框架等失真，考核与引用结论将建立在虚假知识上。

## Key Signals

- 材料清单的依据是"检索结果或记忆中的标题/ID"，尚无官方源逐条核对。
- 候选材料时间戳模糊（只有年份或"最近"）、出处可疑（二手转述、AI 生成的推荐列表）。
- 用户明示保真度要求（如"别给我弄个 1960 年的论文""保真度必须要准"），意味着事后被发现失真的代价远高于逐条验证的成本。

## Essence

保真度的验证单位是"每条材料"而不是"清单整体"——一条失真即可污染整条考核/引用链。四门按成本升序排列，任何一门不过即淘汰或降级；**淘汰与降级都必须留痕**（登记原因与依据），不静默丢弃：留痕既是诚实呈报的义务，也让后续会话不必重查同一条目。相关性核对必须实读标题+摘要，仅凭 ID 或标题联想正是编造的主要入口。

## Approach

1. **门 1 存在性**：每条候选在官方源逐条抓取（论文=arXiv 官方论文页/DOI，项目=GitHub API 仓库元数据），确认 ID→标题→作者链一致；官方源某通道失败时换同源通道（如 arXiv export API 连接失败 → 改 https 主站论文页），禁换二手源定论。
2. **门 2 相关性**：实读标题+摘要，与任务主题逐条比对；判"无关"必须给出摘要依据（如实查为人形机器人运动优化论文，与智能体无关）→ 淘汰。
3. **门 3 时间窗**：用官方提交日期（首次提交，非最后修订）对照窗口（如"近 1 年"），窗口先落为具体日期边界再比对；真实但超窗的材料不混入也不丢弃 → 登记"超窗候选"待用户裁决。
4. **门 4 质量门槛**：项目类核对 stars 数/维护方（大厂官方组织）/性质（框架 vs 工具）；论文类核对出处等级（arXiv/顶会）。逐条记录达标证据（stars 数、org 名等可复查数字）。
5. 清单定稿只收"四门全过"条目；每条登记：结论（入选/淘汰/超窗候选）+ 判定依据 + 官方源链接，构成可复查的验收记录。

## Faster Next Time

- 一句话决策：先逐条过四门再定清单，禁止"先凑满数量再补验证"。
- 警告信号：凭记忆能"背出"论文标题/ID 时最危险——正是编造高发区，必须强制官方源核对；一旦发现某条 ID 指向完全不同主题的内容，立即怀疑同批材料的其余条目。
- 处置三分类：无关（淘汰）、超窗（降级候选待裁决）、低质（淘汰附门槛依据）——比二分类多保留一条可复议路径。
- 渠道故障不影响验证义务：官方源主通道失败就换同源备用通道，原文错误照常留痕。

## Applicability Boundaries

- 适用：任何"外部材料清单纳入"场景——学习考核材料、参考文献、依赖选型、竞品清单、经验引用源。
- 不适用：材料仅为内部草稿占位且明确标注"未验证"、不进入任何决策链；用户已提供逐条核验过的清单（复核成本可酌减，存在性门仍建议保留）。
- 边界：四门通过 ≠ 内容深度合格，只保证"真实、相关、合窗、达标"；掌握深度仍由后续考核/精读环节把关。
- 与相邻经验的分工：任务链第 0 步的"结构性前提证伪与暂停上报"见 2026-11-06-verify-claimed-prerequisites-before-research；"目标框架 ≠ 学习材料"的用途分离见 2026-11-06-multi-purpose-resource-threshold-separation；学习成果入库的五要素格式见 2026-11-06-learning-artifact-five-element-sedimentation。

## Evidence or Examples

- 实录（2026-11-07）：候选论文④ 2501.12594 未验证即列入 → arXiv 官方页实查为《A 3-Step Optimization Framework with Hybrid Models for a Humanoid Robot's Jump Motion》（cs/Robotics，人形机器人）→ 淘汰，编造风险被拦截；候选⑤ Agent Workflow Memory（2409.07429）真实且主题相符，但提交于 2024-09，超"近 1 年"窗口约 2 个月 → 登记"超窗候选"待裁决；microsoft/autogen 经 GitHub API 实证 61,734⭐、官方组织维护 → 通过；论文 2509.02547（Agentic RL Survey）、2504.01990（Foundation Agents）、2501.06322（Multi-Agent Collaboration Mechanisms）逐条实读标题+摘要后入选。
- 渠道实录：`http://export.arxiv.org/api/query` 连接失败（原文留痕），`https://arxiv.org/abs/<id>` 可达，同源换通道完成全部验证。