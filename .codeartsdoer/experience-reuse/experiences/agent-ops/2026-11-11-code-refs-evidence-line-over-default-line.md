---
id: 2026-11-11-code-refs-evidence-line-over-default-line
title: 知识文档修订 code_refs 的取证行选择：内容证据行优先于默认标题行——事实断言定位法
category: agent-ops
nature: decision
created_at: 2026-11-11T01:02:16
updated_at: 2026-11-11T01:02:16
tags: [code-refs, 取证行, wiki修订, 证据锚定, subagent交付]
keywords: [code_refs 取证行, 证据行优先, 标题行默认值, 关键文件清单条目, patch JSON 修订, 行号实读核实, 事实断言定位, 存在性指针, 交付要点注明, 知识文档溯源]
problem_patterns:
  - 为"关键文件与位置"类清单小节的新文件条目写 code_refs 时，按派工单默认指引一律取第 1 行/标题行，引用只证明文件存在、无法支撑条目新增的内容级陈述
  - 同一文件内多行都可作为引用时随手取首行，code_refs 退化为存在性指针，上游校验时无法判断条目陈述内容的真实来源
source_sessions: [ses_e39b184bcffe7JHUCjxIgMW3Xn]
project: Date
severity: low
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-11-subagent-wiki-patch-code-refs-read-verify, 2026-11-09-subagent-patch-code-refs-baseline-fallback, 2026-11-08-wiki-section-tiered-revision-judgment-contract, 2026-11-08-wiki-section-revision-patch-json-mode]
---

# 知识文档修订 code_refs 的取证行选择：内容证据行优先于默认标题行——事实断言定位法

## Scenario

以 subagent 身份承接知识文档/Wiki 小节级修订派工（patch JSON 载体），修订"关键文件与位置"类清单小节，为本轮新增的文件条目附 `code_refs`（`文件相对路径:行号`，行号必填、实读核实后填写）。派工单常附默认指引："新文件一般为 1 或标题行"——这是省事惯例而非硬约束。本轮变更源是三篇全部新增（added）的文档，条目对每篇做了内容级陈述（编译/测试/运行命令基线、环境口径、路由规则）。修订者独立执行、无法中途确认。

## Key Signals

- 派工单默认指引"一般为 1 或标题行"是给纯存在性条目的兜底，条目一旦转述了文件里的具体内容（命令、口径、规则、机制），标题行就与陈述脱节。
- 清单条目出现内容级动词宾语（"声明了 XX 命令""口径为 XX""路由规则为 XX"）→ 强信号：该条目需要内容证据行。
- 上游存在"未实读引用一律回退"的裁决惯例（见 baseline-fallback）——引用能否被保留，取决于能否证明"实读了且指向所述内容"。

## Essence

code_refs 的取证行应与条目承载的**事实断言同位**：条目写了"文件里说了什么"，就引用那一行；标题行只证明文件存在，证据行才能证明"写进小节的内容来自文件的哪里"。默认指引（一般为 1 或标题行）仅在条目为纯存在性陈述时适用。取证行选得准，上游无需重读源文件即可校验引用，溯源链从"存在性指针"升级为"内容可校验证据"。

## Approach

1. 实读新文件全文，圈出清单条目将要陈述的每个事实断言（命令基线、口径声明、规则表、机制定义），标记其在文件中的行号。
2. 条目为内容级陈述 → code_refs 取断言所在行；多条断言时取最能支撑该条目主旨的一条（受引用条数约束时按主旨取舍）。
3. 条目仅为存在性陈述（只说"某主题文档"）→ 按默认指引取标题行/首行兜底。
4. 交付消息逐条注明"文件:行号（证据内容）"，让上游按"实读为证"直接放行，无需回读源文件复核。
5. 引用集保持最小证据集：不为凑数多引、不主动扩充引用集（防止触发消费端回退裁决）。

## Faster Next Time

- 一行决策规则：条目转述了文件内容 → 引那一行；条目只说"有这么个文件" → 才用标题行。
- ROI：证据行使引用免于"未实读回退"裁决，省去一轮引用被裁剪后的重新交付；小节修订的可信度由"引用了文件"变为"引用了文件的确切依据"。
- 警惕信号：发现自己对默认指引照单全收而未实读 → 停；条目含命令/规则/口径转述却引的是标题行 → 引用与陈述脱节。
- 反模式：所有新文件一律 `:1`；为"更完整"把同一文件多行全部塞进 code_refs（过度覆盖，触发回退）。

## Applicability Boundaries

- 适用：知识文档/Wiki 清单型小节（关键文件与位置、参考文档清单类）为新文件条目附 code_refs 的 replace_content 场景；上游设有"实读为证"裁决惯例的 patch 流水线。
- 不适用：代码符号文件（应用符号骨架定位而非行号猜测）；条目式短文档的"第 N 条 = 行 N"锚点构造（行号由条目序号直接映射，见 tiered-revision-judgment-contract）；line_number_only 场景（引用集以检索基线原值为准，见 baseline-fallback）；目录类条目（无行可选，存在性核实即可，见 code-refs-read-verify）。
- 与相邻经验分工：code-refs-read-verify 管"取证顺序四步检查单"（读什么、什么顺序）；baseline-fallback 管"消费端对未实读扩充引用的回退裁决"（编排者视角）；tiered-revision 管"节级 action 分流与条目式行号锚点"；本条管"同一文件内取证行的选择准则"（subagent 侧，证据行 vs 默认行），按取证环节互补不重叠。
- 证据等级：单次成功闭环（三文件证据行 + 交付逐条注明），无失败对照；"纯存在性条目取标题行兜底"分支在本次未实际触发，属推断补全，待同类任务复用检验。

## Evidence or Examples

- 来源会话：ses_e39b184bcffe7JHUCjxIgMW3Xn（@general subagent，project-knowledge/tooling_and_environment 文档 3 小节修订，变更源为 3 篇全部 added 的文档）。
- 派工单默认指引原文："code_refs 格式 文件相对路径:行号，行号必填（实读核实后填写，新文件一般为 1 或标题行）"。
- 实际取证行（均非标题行）：`06_开发工具/工具链说明.md:8`（编译基线命令）、`06_开发工具/Windows本机仿真环境启动流程.md:3`（口径行）、`06_开发工具/Kali环境等效方案与回退机制.md:8`（路由规则表）。
- 交付留痕：patch JSON 落盘后，最终消息逐条注明"行号均已实读核实：…:8（编译基线命令）、…:3（口径行）、…:8（路由规则表）"，上游无需回读即可校验。
- 一致性佐证：baseline-fallback 的保留实证（项目事实表.md:22 事件钩子、:24 维护机制 §9）同为内容证据行，印证上游按"实读证据行"放行的裁决惯例。