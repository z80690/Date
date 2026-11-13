---
id: 2026-11-08-wiki-section-tiered-revision-judgment-contract
title: Wiki 受影响小节的节级分流判定：同层面才改正文、其余仅校行号——纯文档行号锚点与 code_refs 保守原则
category: agent-ops
nature: methodology
created_at: 2026-11-08T10:16:13
updated_at: 2026-11-08T10:49:52
tags: [wiki修订, 节级分流, 派工判定, code_refs, 行号锚点]
keywords: [同层面判断, replace_content, line_number_only, 符号骨架空, 行号锚点, code_refs 保守原则, 判定预判, patch JSON, 小节修订派工, 只读 subagent]
problem_patterns:
  - 公约条目合并/新增波及多个小节后，不知哪些小节要重写正文、哪些只需核对行号引用，默认全量重写会向技术栈/关系等属性型小节引入噪音，漏改枚举型小节则残留旧口径
  - 纯 .md 文档符号骨架为空，code_refs 行级引用无从下手，误用统一的文件级 :1 应付所有引用
source_sessions: [ses_e489395f4ffekheN9UTSC6iPDv]
project: Date
severity: low
quality_score: 84
hit_count: 6
last_hit_at: 2026-11-13T13:02:13
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-08-wiki-section-same-layer-action-criteria, 2026-11-08-wiki-section-revision-patch-json-mode, 2026-11-08-wiki-update-script-behavior-contract-blindspots, 2026-11-08-subagent-patch-field-drift-silent-content-loss, 2026-11-07-dispatch-brief-embedded-fact-pack]
---

# Wiki 受影响小节的节级分流判定：同层面才改正文、其余仅校行号

## Scenario

以只读 subagent 身份接收 Wiki 小节级修订派工（本例修订 `codebase-knowledge/官方文档与协作规范.md` 的 5 个受影响小节），源文档为 `docs/项目协作公约-最终稿.md`（6 行纯文档，条目式规矩）。派工单内嵌四类材料：变更文件最新全文（权威新口径）、口径变化要点（旧→新逐条对照）、受影响小节当前内容、符号骨架声明（空）与模板小节写法规范。任务边界：只做逐节修订判断并输出结构化 patch JSON，禁止写入任何文件。

## Key Signals

- 同一条目变化波及 5 个小节，但波及性质不同：概述/架构设计小节正文**枚举了公约条目名**（旧口径残句："禁自建定时任务"已非独立条目、缺新条目"执行节制"）；而技术栈/编码规范/关系小节只是被"波及"——正文关注点是技术栈、格式约定、依赖关系，条目语义变化不落在这三个层面。
- 符号骨架为空：`.md` 纯文档无代码符号，行级引用只能靠行号锚点映射——"第 N 条规矩 = 行 N"（6 行文件，第 4/5/6 条各对应行 4/5/6）。
- 派工单直接给出每个小节的预判 action（replace_content / line_number_only）与判定理由，subagent 逐节验证预判后执行，而非重新发明判定。
- 输出契约：严格 JSON 直出（无 markdown 包裹、直接以 `{` 开头），`section_title` 逐字复制 `##` 后标题文本，frontmatter 与小节标题禁改。

## Essence

**受影响 ≠ 需要改正文**。节级判定准则是"变更是否与该小节已有关注点同层面"：正文承载条目口径的枚举型/叙述型小节（概述、架构设计）→ `replace_content` 按新口径重述枚举；只被波及但关注点未变的属性型小节（技术栈、编码规范、关系）→ 格式与关系性质不变时仅 `line_number_only` 维护 `code_refs`，正文置 null。纯文档以行号锚点代替符号骨架完成行级定位；`code_refs` 遵循保守原则：**文档集合保持与原索引一致**，仅新增有行级依据的引用，不变动未变更文档的引用。这补充了"全部联动换口径"原则的另一半——全部进 patch ≠ 全部改正文，patch 内部还要按层面分流。

## Approach

1. **派工单预置四要素**：变更文件最新全文（权威新口径）+ 口径变化要点（旧→新逐条）+ 受影响小节当前内容 + 符号骨架声明；纯文档显式声明"骨架空"并给出行号锚点映射（第 N 条 = 行 N）。
2. **逐节同层面分流**：对每个受影响小节问"该小节正文是否承载了变化的口径？"——是 → `replace_content` 按新口径重述枚举（保持其余句子不动、控制字数）；否（格式未变/关系性质未变/层面无关）→ `line_number_only`，`new_content` 为 null，仅核对 `code_refs`。
3. **行号锚点构造**：纯文档按"第 N 条 = 行 N"映射；`code_refs` 用 `文件:行号` 形式；原引用未变更的保持原行号，新增引用必须有行级依据（如编码规范小节补 `:6` 以体现单行成条格式的证据）。
4. **判定预判式派工**：派工单直接给出每节的预判 action + 理由，subagent 只做验证与执行——压缩字段名/动作漂移空间，判定结论可追溯（谁预判、谁验证）。
5. **输出与交付边界**：修订者禁写文件，patch JSON 交上游合并脚本统一应用（分离模式与落盘契约见 wiki-section-revision-patch-json-mode）。

## Faster Next Time

- ROI：5 个受影响小节只重写 2 个枚举型小节，3 个属性型小节仅校行号——省去无效重写与合并后的人工复核；行号锚点让纯文档 `code_refs` 一次到位，不再用文件级 `:1` 应付。
- 判定口诀：正文含条目枚举 → 改；只受波及但格式/关系未变 → 只校行号；行号依据 = "第 N 条 = 行 N"。
- 警惕信号：受影响小节清单很长时不要默认全部 `replace_content`——先做同层面分流；派工单已有预判时不重新发明判定，只验证预判是否成立；`code_refs` 引用集合发生变化时必须有行级证据支撑。

## Applicability Boundaries

- 适用：纯 Markdown 文档库、按 `## 标题 <!-- category:xxx -->` 组织、patch 由合并脚本统一应用的 Wiki 小节修订派工；源文档为短行数条目式文档（"第 N 条 = 行 N"可直接映射）。
- 不适用：含代码符号的源码文件（应使用符号骨架定位而非行号锚点）；授权直改的普通文档编辑；条目增删导致行数变化、行号整体位移的场景（锚点需重新映射，不能沿用旧行号）。
- 与相邻经验分工：`wiki-section-same-layer-action-criteria` 与本条判据同源（同层面分流），其独有价值在逐句比对细则与派工清单外隐性失真自查（元层面小节概念、数字条数/条目名/格式词快捷判据）；本条管只读 subagent 场景的完整执行契约——判定预判式派工（上游预判+下游验证）、纯文档行号锚点（"第 N 条 = 行 N"）、code_refs 保守原则。同一小节在不同轮次变更下 action 结论可不同（编码规范小节在 7→6 大改版轮判 replace、在条目合并轮判 line_number_only），差异来源是当轮变更实文不同而非判据冲突，选型时以当轮变更实文逐句比对为准；`wiki-section-revision-patch-json-mode` 管"建议-合并分离 + 实读核实口径 + 全部进 patch"；`wiki-update-script-behavior-contract-blindspots` 管合并脚本盲区（H1/frontmatter 需编排方合并后补正）；`subagent-patch-field-drift-silent-content-loss` 管合并前的字段归一校验。
- 证据等级：单次实战闭环（5 节判定 + patch JSON 输出结构完整合规）；合并应用结果在本 trace 之外，分流规则在多场景下的稳定性待复用检验。

## Evidence or Examples

- 源会话 ses_e489395f4ffekheN9UTSC6iPDv（@general 修订 subagent，trace 内联提供）。
- 分流判定结果：概述/架构设计 → `replace_content`（枚举旧口径："禁自建定时任务"已并入"规矩层冻结"、缺"执行节制"）；技术栈/编码规范/关系 → `line_number_only`（公约格式仍 6 行单行成条、约束关系性质未变、内容变化不涉技术栈层面）。
- 行号锚点实例：`docs/项目协作公约-最终稿.md` 共 6 行，第 4 条 = 行4、第 5 条 = 行5、第 6 条 = 行6。
- code_refs 实例：概述/架构设计/技术栈三小节保持三文件各 `:1`；编码规范补 `docs/项目协作公约-最终稿.md:6`；关系保持公约 `:1` + 最佳实践 `:1`；Skills 清单与最佳实践引用未变更、行号不动。