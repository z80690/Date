---
id: 2026-11-11-subagent-wiki-patch-code-refs-read-verify
title: 知识文档修订派工的 code_refs 事前实读取证流程与 patch JSON 落盘契约
category: agent-ops
nature: technique
created_at: 2026-11-11T00:43:26
updated_at: 2026-11-11T00:50:39
tags: [agent-ops, code-refs, wiki-revision, subagent, evidence-verification]
keywords: [code_refs 行号实读, patch JSON 契约, 子智能体修订, 知识文档修订, 目录存在性核实, 中文目录乱码交叉验证, section replace_content, 派工修订]
problem_patterns: ["修订知识文档需附 code_refs 时凭记忆或旧文档推断行号导致引用失真", "目录列表输出中文乱码时误判目标目录不存在"]
source_sessions: ["ses_e39b4bbdcffe7zGxODTIRXvypD"]
project: Date
severity: medium
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["2026-11-09-subagent-patch-code-refs-baseline-fallback", "2026-11-08-wiki-section-tiered-revision-judgment-contract", "workflow/2026-11-11-wiki-stat-count-drift-recount-on-revision"]
---

# 知识文档修订派工的 code_refs 事前实读取证流程与 patch JSON 落盘契约

## Scenario

主 Agent 以子智能体（如 general）承接"项目规范知识文档（wiki）增量修订"派工单，要求逐小节修订并附 `code_refs`（格式 `文件相对路径:行号`，行号必填、实读核实后填写），最终以结构化 patch JSON（`wiki_file` + `patches[section_title/action/new_content/code_refs]`）落盘到约定临时路径。此类派工高频出现，行号引用失真是最典型的返工与失真来源。

## Key Signals

- 派工单显式给出受影响小节、变更文件列表、patch JSON 格式契约与落盘路径——这是"行号必须实读"的强信号。
- 列目录命令输出中文目录名乱码（如 `02_软件源码` 显示为 `02_ศํผ�ิดย๋`），容易误判目录缺失或环境异常。
- 若引用行号来自旧文档记载或记忆而非本次实读，后续 patch 应用时行号与实际内容错位。

## Essence

code_refs 的可信度来自"取证顺序"而非"记得多少"：主文件全文实读定位新条目行号 → 被引文件（需保留的旧引用）核对行号仍有效 → 新增目录类条目用列表命令核实存在性 → 实例文件抽读补行号。目录名乱码是 Windows 下外部 CLI 子进程 ANSI 解码中文的显示层失真，不影响目录真实存在——应以权威文件记载（如 README 目录池表）+ 子内容存在（如该目录下有源码/文档文件）交叉验证，不重试、不阻塞。

## Approach

1. 先实读主修订对象相关的全部新增/变更文件全文（确定新条目的 code_refs 行号来源）。
2. 对派工单要求保留的旧引用，实读被引文件确认行号与语义仍有效；失效则改写或丢弃，不沿用旧值。
3. 新增"目录/位置类"条目用一次性列表命令（列目录 + 抽查子内容）核实存在性，再写 code_refs。
4. 遇目录名乱码：不重试乱码命令，改用"权威文件记载 + 子内容存在"两路证据交叉确认。
5. 按契约将 patch JSON（UTF-8 无 BOM）写入派工单指定临时路径，每个 patch 含 `section_title`/`action`（同层面变更用 `replace_content`）/`new_content`/`code_refs` 四字段。
6. 最终消息只返回：patch 文件路径 + 各小节修订要点各一句话，不粘贴 patch 全文。

## Faster Next Time

- 取证检查单：主文件全文 → 旧引用有效性 → 目录存在性 → 实例抽读，四步走完才允许落盘 patch。
- 行号一律从"本次实读输出"抄写，禁止从待修订文档自身的旧 code_refs 直接复制。
- 看到中文乱码先怀疑解码失真而非目录缺失，用第二条证据链交叉验证，节省 2-3 轮无谓重试。
- 交付消息保持"路径 + 每小节一句话"，避免长内容回流污染主 Agent 上下文。

## Applicability Boundaries

- 适用：派工修订项目知识库/wiki 文档并要求附 code_refs 的子智能体任务；主 Agent 侧为 patch 应用方校验提交内容时也可参照取证检查单。
- 不适用：代码 patch（diff/行号语义不同）、无引用要求的纯笔记撰写。
- 乱码交叉验证基于 Windows 环境外部 CLI 中文输出失真场景；其他平台的乱码成因需先另行定位。
- 单次成功样本（无失败对照），取证顺序的完备性未经反例检验。

## Evidence or Examples

- 来源会话：ses_e39b4bbdcffe7zGxODTIRXvypD（documentation_system 知识文档 4 小节修订派工）。
- 实读链路：README.md 全文（32 行，目录池表定位 00-09 各目录用途）→ notes/知识库索引.md 登记表 → notes/知识库初始化.md（8 行，确认旧引用三分约定行号仍有效）→ 一次性 bash 列目录（00-09 目录池实存；02 目录名乱码）→ 08_交付文档/功能说明与恢复边界.md 抽读 1-5 行（补版本行引用）。
- 落盘产物：`C:\Users\Administrator\Desktop\Date\.codeartsdoer\temp\patch_docsys.json`，write 成功，最终消息含路径 + 4 小节要点各一句。