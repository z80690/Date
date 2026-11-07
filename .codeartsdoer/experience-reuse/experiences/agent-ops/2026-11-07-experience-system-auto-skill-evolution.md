---
id: 2026-11-07-experience-system-auto-skill-evolution
title: 平台 idle 后台技能演进产物的定性处置与知识沉淀双源边界
category: agent-ops
nature: methodology
created_at: 2026-11-07T09:17:47
updated_at: 2026-11-07T09:49:33
tags: [agent-platform, skill-evolution, knowledge-dedup, asset-triage]
keywords: [generated-skills, 后台演进, idle复盘, 技能沉淀, 双源冲突, 查重, 更新优先于新建, 资产定性, skill_manage, 演进工作区]
problem_patterns: ["提交前 status 终扫发现来历不明的技能目录，误判为垃圾或攻击产物直接删除", "同一主题的知识同时沉淀到演进工作区与正式技能库，形成双源后续维护分叉", "后台代理沉淀知识时未先查存量载体，重复创建已有技能的副本"]
source_sessions: [ses_e4c75b385ffejT7VS1xOgDQLc2]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["agent-ops/2026-11-06-codeartsdoer-skill-market-registry.md", "agent-ops/2026-11-06-precise-staging-bidirectional-consistency-gate.md", "2026-11-07-experience-skill-auto-evolution-channel"]
---

# 平台 idle 后台技能演进产物的定性处置与知识沉淀双源边界

## Scenario

长会话进入 idle 阶段后，平台后台演进代理（background-evolve-skills 类机制）会复盘会话轨迹，把可复用模式沉淀为技能文档；与此同时，主会话执行代理在提交前做 status 终扫时，会在工作区发现"来历不明"的技能目录。两类角色互不知情，若执行代理按"未知文件=垃圾"处置会误删资产，若后台代理不查重会造成知识双源。

## Key Signals

- `git status` 出现未跟踪的技能目录（如 `skills/<name>/SKILL.md`），非当次任务产物。
- 目录内容与本会话实战经验一一对应（如编码怪癖、平台注册机制、流程契约），特征是"刚踩过的坑被立即文档化"。
- 平台用户级目录下存在演进工作区（如 `~/.codeartsdoer/evolve/skill_evolution_workspace/generated-skills/`），是此类产物的真实来源。
- 后台代理的调用链特征：`skills_list`（查重）→ `skill_view`（对照）→ `skill_manage`（更新/新建）。

## Essence

1. generated-skills 类目录是平台 idle 复盘的**合法知识资产**，处置前先定性、不先删除。
2. 后台演进的准入纪律是：先全量列出既有技能查重 → 再逐个对照内容 → **更新优先于新建**（编辑校验失败时降级用 patch 类动作）。
3. **双源边界**：某主题已有正式技能载体（项目技能库/市场技能）时，演进目录不得重复创建同一主题，避免双源冲突与后续维护分叉。

## Approach

1. 发现未知技能/配置目录：先读 SKILL.md 定性（来源、内容主题、与既有资产的关系），再决定入库、保留或上报，禁直接删除。
2. 自己沉淀知识前：同时查两个载体——演进工作区（generated-skills）与正式技能库（skills/），同主题只保留一处权威源。
3. 更新既有技能：先 `view` 全文对照找增量缺口，用最小修改（patch/局部替换）落笔，不整篇重写。
4. 命中"已有正式载体"的主题时：不新建副本，在提交/汇报中说明归属，留指针即可。

## Faster Next Time

- 看到"来历不明"文件先按"平台后台机制产物"假设核查（查演进工作区、对内容主题），一次定位避免误删。
- 知识沉淀前做双载体查重（成本一次 list 调用），防双源返工。

## Applicability Boundaries

- 适用于具备 idle 后台演进/复盘机制的平台（本机实证为 CodeArts evolve 工作区）。
- 无此机制的平台上，"来历不明文件"仍走人工核实流程，但"沉淀前双载体查重、更新优先于新建"仍通用。
- 经验属于 Agent 平台运行层（agent-ops），不覆盖一般构建环境问题。

## Evidence or Examples

- 本会话实证：提交前终扫发现 3 个自动生成技能目录（平台注册机制、SDD 流水线契约、Windows/PowerShell 怪癖），SKILL.md 内容与会话踩坑一一对应，定性为合法资产入库。
- 后台代理对既有技能 `windows-git-powershell-quirks` 用 patch 方式更新（edit 动作因 frontmatter 校验失败，降级 patch 成功），并因"考核双官模式已有正式技能 learn-gate"而拒绝在 generated-skills 重复创建——双源边界的正面与反面各有实证。