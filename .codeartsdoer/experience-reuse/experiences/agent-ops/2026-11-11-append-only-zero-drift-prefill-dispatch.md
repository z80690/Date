---
id: 2026-11-11-append-only-zero-drift-prefill-dispatch
title: 登记区末尾追加型变更的零漂移快捷通道：模板级预填派工 + 新增引用实读核实前置
category: agent-ops
nature: technique
created_at: 2026-11-11T09:54:31
updated_at: 2026-11-11T10:46:07
tags: [wiki修订, 预填派工, 零漂移, code_refs, subagent交付]
keywords: [末尾追加, 零漂移, line_number_only, 模板预填, code_refs 建议集, 实读核实前置, 登记区, 变更日志, patch JSON, 判定预判派工]
problem_patterns:
  - 登记类文件（变更日志/索引登记表）末尾追加条目后，不确定既有小节 code_refs 行号是否漂移，默认全部小节重新逐条核行号造成重复劳动
  - 派工单只预判 action 而不预填引用集与 JSON 骨架时，subagent 有空间自行扩充引用或漂移字段，编排者需事后逐条裁决回退
source_sessions: [ses_e37b65e0affe3RgzNLrsynEdvw]
project: Date
severity: low
quality_score: 80
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-08-wiki-section-tiered-revision-judgment-contract, 2026-11-09-subagent-patch-code-refs-baseline-fallback, 2026-11-11-subagent-wiki-patch-code-refs-read-verify, 2026-11-11-code-refs-evidence-line-over-default-line, 2026-11-07-dispatch-brief-embedded-fact-pack, 2026-11-07-dispatch-brief-embedded-experience-guidance, 2026-11-11-wiki-verbatim-consistency-line-number-only]
---

# 登记区末尾追加型变更的零漂移快捷通道：模板级预填派工 + 新增引用实读核实前置

## Scenario

主 Agent 编排 Wiki 小节级修订派工（本例 S2 文档级修订，3 个受影响小节），变更源为登记类文件的最高频变更形态：`notes/知识库索引.md` 变更日志区**末尾追加** 2 条登记行，文件其余部分未变。派工单由编排者预填到"模板级"：逐节预判 action + 理由、建议 code_refs 全集（含 2 条指向新增文件的新引用 `:1`）、除 `new_content` 外全部字段实值的 JSON 骨架、主 Agent 已实读确认的权威事实包、内嵌检索到的任务经验指导。subagent 禁写文件，只输出 patch JSON，独立执行、无法中途确认。

## Key Signals

- git hunk 显示改动仅落在登记文件末尾（第 118–119 行追加 2 行）——登记区追加型变更的判别信号。
- 派工单权威事实包显式声明"引用行经实读核对行号未漂移"——漂移疑虑已在派工侧闭环，subagent 无需逐条重验既有引用。
- 派工单内嵌经验指导"扩充项逐一实读核实"，且建议 code_refs 含 2 条新增文件引用——新引用须实读取证后方可进入 patch。
- 对照信号：同链路前一日会话中，subagent 在 line_number_only 场景自行扩充 2 条未实读引用，被编排者回退（见 baseline-fallback）——越界扩充是该链路已知风险。

## Essence

**行号是否漂移取决于变更位置而非变更本身**：登记区末尾追加不移动既有行号 ⇒ line_number_only 小节的基线原值引用必然仍准确，可免逐条重验——"末尾追加 → 零漂移"是一等快捷判据。在此基础上，派工单把判定（逐节 action + 理由）、引用（建议 code_refs 集）、结构（JSON 骨架）三件套全部预填，subagent 的自由度收敛到唯一必需环节——对新增引用做实读取证（读新文件头部确认标题与性质）——从"重新发明判定"降级为"验证 + 组装"。预填抑制越界扩充的方式是把纪律前置成结构：引用集以"建议 + 须实读核实后进入"的形式给出，边界在派工单里画好，subagent 既无自行扩充的动机，又保留了核实职责；同链路实测从"事后回退裁决"变为零偏差一轮收敛。

## Approach

1. **编排者判别变更形态**：git hunk 显示改动全部落在登记文件末尾（追加行）→ 判定零漂移，派工单以权威事实包显式声明"行号未漂移"；条目增删发生在文件中部则行号整体位移，此快捷通道不适用。
2. **派工单三件套模板级预填**：逐节预判 action + 同层面理由 → 建议 code_refs 全集（新引用标注"建议"并注明须实读核实）→ 完整 JSON 骨架（除 `new_content` 外字段全部实值）。
3. **权威事实包前置**：主 Agent 实读确认的现状事实（篇数构成、新文件清单、行号核对结论）逐条编号写入派工单，声明"写正文必须与此一致，禁止自行编造"。
4. **subagent 执行最小核实**：仅对建议集中的新增引用实读新文件头部（`文件:1` 锚点只需标题行证据，确认标题与性质和条目构成陈述相符）；既有引用按"行号未漂移"声明直接保持基线原值。
5. **组装输出**：严格 JSON 直出；`new_content` 按权威事实包改写（旧数字删除不留残句），line_number_only 小节 `new_content` 为 null；产出与预填模板逐字段一致即交付。

## Faster Next Time

- 判定口诀：末尾追加 → 零漂移 → line_number_only 免重验；中部增删 → 行号位移 → 逐条重验或重映射。
- 派工 ROI：三件套预填后 subagent 一轮收敛（本例 3 条消息：2 次新文件头部实读 + 1 次组装输出），无回退、无字段漂移、无引用越界，省去编排者事后对照基线逐条裁决扩充项。
- 抑制过度覆盖倾向的结构化手段：把 baseline-fallback 的事后"裁剪回退"变为事前"建议引用集 + 实读核实前置"——宁可编排者多花一步预填引用集，也不要事后裁决。
- 警惕信号：派工单只有 action 预判而没有建议引用集时，subagent 可能自行补引用；权威事实包缺失时预填依据不可靠，先实读再派工。

## Applicability Boundaries

- 适用：登记类/日志类文件（变更日志区、索引登记表）的末尾追加型增量修订；判定预判 + 建议-合并分离的 Wiki patch 派工流水线；同链路既往出现 subagent 越界扩充引用、需事前抑制的编排场景。
- 不适用：条目增删发生在文件中部导致既有行号位移（须逐条重映射）；含代码符号的源码文件（符号骨架定位）；新增文件条目含内容级陈述（取证行应选内容证据行而非标题行，见 evidence-line 经验）；主 Agent 未实读确认现状时。
- 与相邻经验分工：tiered-revision-judgment-contract 管"逐节同层面分流 + 判定预判式派工"通用契约，本条管其在末尾追加型变更下的最简形态（零漂移判据 + 引用集与骨架的模板级预填）；baseline-fallback 管编排者事后回退裁决，本条管事前预防；code-refs-read-verify 管 subagent 侧取证顺序四步检查单，本例是其最简实例（仅 2 次新文件头部实读）；evidence-line 管取证行选择，本例新引用均为纯存在性构成条目故取 `:1` 合规；dispatch-brief-embedded-fact-pack / embedded-experience-guidance 管派工单内嵌事实包与经验指导，本条是其在登记类增量场景的组合应用。
- 证据等级：单次平滑闭环（零偏差、3 条消息收敛），无失败对照；"预填抑制过度覆盖"基于同链路前后两次会话对照归纳（一次越界回退、一次零偏差），非受控实验，待复用检验。

## Evidence or Examples

- 源会话 ses_e37b65e0affe3RgzNLrsynEdvw（@general subagent，project-knowledge/documentation_system 3 小节修订，S2 文档级）。
- 变更形态：notes/知识库索引.md 变更日志区第 118–119 行追加 2 条登记行（DevSidecar+Tor攻防环境搭建笔记、攻防环境优化建议，2026-11-11，状态=现行），文件其余部分未变。
- 权威事实包（5 条）：notes/ 实存 22 个文件 = 根级 15 + 浓缩版/ 3 + 档案区/ 4；旧口径 20 篇/根级 13 篇过期；第 3 行（唯一登记入口）与第 26 行（公约三副本登记）行号未漂移；两层组织与三分约定未变，本次仅为组织结构内条目新增。
- 派工预填结论：关键文件与位置 → replace_content（22 篇/根级 15 篇，2 篇新笔记入列），code_refs 建议 ["notes/知识库索引.md:3", "notes/攻防环境优化建议.md:1", "notes/DevSidecar+Tor攻防环境搭建笔记.md:1"]；架构与约定 → line_number_only 保持 ["notes/知识库索引.md:26"]；开发者应遵守的规则 → line_number_only 保持 ["notes/知识库索引.md:3"]。
- subagent 执行留痕：实读 2 个新文件头部各 3 行（确认性质："学习阶段输出+历史复盘记录"/"优化建议报告"）后输出 patch JSON，与预填模板逐字段一致，零扩充、零漂移。
- 前后对照：ses_e4405534affeu8pLGAbuG7Iwh9（前一日）line_number_only 小节自行扩充 2 条未实读引用被编排者回退；本会话预填 + 前置核实后零越界——同链路对照支持"预填抑制过度覆盖"。