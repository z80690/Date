---
id: 2026-11-10-skill-evolution-review-dedupe-first-patch-existing
title: 技能库演化审查三级覆盖判定协议：先查重再通读后补差，补丁优先于新建
category: agent-ops
nature: methodology
created_at: 2026-11-10T22:04:10
updated_at: 2026-11-10T22:08:06
tags: [技能演化, 查重判定, 技能补丁, 沉淀纪律, description同步]
keywords: [background-evolve-skills, idle-scan, skills_list查重, skill_view通读, skill_manage补丁, 优先更新现有技能, 技能碎片化, 触发词同步, 覆盖判定, 不动也是结论]
problem_patterns:
  - "会话末尾收到技能演化审查任务时，未查既有技能就新建技能，产生与既有技能重叠的碎片化条目"
  - "只比对技能 description 就下覆盖结论，误判'已覆盖'或'缺口'，补错对象或漏补真缺口"
  - "skill_manage 只补正文不改 description，新增内容检索不可达，补丁等于白做"
source_sessions: [ses_e3a448aefffeqBjZRM1XamKpG4]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["agent-ops/2026-11-10-batch-parallel-workdir-discipline-root-dir-residue"]
---

# 技能库演化审查三级覆盖判定协议：先查重再通读后补差，补丁优先于新建

## Scenario

会话结束后由 idle-scan 自动触发的技能库演化审查任务（实例：background-evolve-skills 类指令）：输入为一段完整会话轨迹，要求从中识别可复用模式并沉淀到 generated-skills 技能库。任务自带硬约束：动手前必须先 skills_list 查重、优先更新现有技能（edit/patch）而非新建（create 仅在无既有技能覆盖时使用）、禁改技能库之外的文件、禁用 bash。一次审查通常面对轨迹中的多种模式类型（踩坑型/工作流型/决策型），须逐一定载体归属。

## Key Signals

- 任务描述自带硬顺序："Before creating a new skill, call skills_list to see existing generated skills, then skill_view for any that overlap"——顺序不可跳步，查重在动手之前。
- 轨迹中部分模式已有既有载体覆盖：既有技能正文、技能 description 已承载的口径、项目机制文件（规则/机制文档）——直接新建会产生碎片化重复。
- 两个相邻信号易误判：①description 命中但正文无细节（半覆盖，需读正文核实）；②模式已由项目机制文件承载（此时技能只该留指针，不该展开正文）。

## Essence

演化审查的核心动作不是"把轨迹里所有模式写成新技能"，而是**三级覆盖判定后精准补差**：①查重（skills_list 全列含 description）→ ②通读重叠候选（skill_view 读全文，禁只看 description 下结论）→ ③逐模式判定载体归属——四分支：已有技能正文覆盖→不动；已由项目机制文件承载→不动（技能至多留指针）；现有技能存在缺口→补丁该技能（edit 正文 + patch_frontmatter 同步 description 触发词）；无任何载体→才新建。**"评估后不动"是合法且常见的结论**，一次审查四个模式中两个不动、两个补丁属正常分布。补丁后 description 必须同轮扩充触发词——正文补丁不改 description，等于把内容写进检索不可达区。

## Approach

1. `skills_list` 全列现有技能（名称 + 状态 + description）。
2. 将轨迹候选模式的关键词逐一比对各技能 description，列出重叠候选清单。
3. 对每个候选 `skill_view` 通读全文（可并行），核对正文是否真正覆盖该模式——只看 description 判"已覆盖"是误判高发点。
4. 逐模式做载体归属四分支判定（技能已覆盖 / 项目机制文件承载 / 技能缺口补丁 / 全新建）。
5. 补丁动作成对执行：`skill_manage` action=edit 写正文小节 + action=patch_frontmatter 扩 description 触发词——两步同轮完成。
6. 总结输出固定含三部分：更新了哪些技能及新增小节、哪些模式判定不动及理由、未新建技能的结论（有则写"无需新建"）。

## Faster Next Time

- 一句话协议：**先查重、再通读、后补差——补丁优先于新建，不动也是结论。**
- 警示信号：审查结论为"新建 N 个技能"而未见逐条比对既有技能 description 的动作 → 大概率产生碎片化重复，回退重查。
- description 与正文必须同轮更新：只补正文不改 description，新增内容在后续触发匹配中不可达。
- 判定"已由项目机制文件承载"时，技能侧的正确形态是留一行指针，不是把机制正文复制进技能（双源漂移隐患）。

## Applicability Boundaries

- 适用：技能库演化审查（background-evolve-skills / idle-scan 类自动触发任务）、会话末尾的可复用模式沉淀任务、任何"沉淀前需查重"的库维护场景（经验库/规则库同理）。
- 不适用：技能库外的规则/经验/项目文档维护（此类任务明确禁改项目文件）；首次建库（无既有技能可查重时直接走 skill-writer 类创建流程）。
- 平台标注：本实例在 CodeArts Agent 实测（skills_list / skill_view / skill_manage 工具链）；协议本身为通用 Agent 模式，其他平台替换为等价的列出/读取/更新原语即可。

## Evidence or Examples

- 来源会话：ses_e3a448aefffeqBjZRM1XamKpG4（小智仿真接入工作流接口项目评估 fork #1，2026-11-10，42 条消息）。
- 判定实例四条：①知识库入库流程 → 判"由项目机制文件承载（技能只留指针）"不动；②安全红线处理（红线保留+校验层换位）→ 判"已在既有模式内覆盖"不动；③多视频并行 workdir 陷阱 → 判 web-content-scraping 缺口，补丁正文小节 + description；④spec 阶段原地增量补充模式 → 判 sdd-spec-pipeline 缺口，补丁正文小节 + description。
- 执行实证：skills_list 1 次 + skill_view 2 次（并行）+ skill_manage 4 次（2 次正文 edit + 2 次 description 更新）全部成功返回 ok；最终结论"评估后不动 2 项、更新 2 技能、未新建"。