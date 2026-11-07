---
id: 2026-11-07-write-receipt-not-proof-of-persistence
title: write 成功回执不等于落盘成功，交付级文件写后必须实证存在且非空
category: agent-ops
nature: pitfall
created_at: 2026-11-07T18:21:54
updated_at: 2026-11-07T18:51:27
tags: [落盘验证, 工具回执, 静默失败, 写后必验, 交付质量, 交付纪律]
keywords: [write 回执, 落盘失败, 静默失败, 列目录验证, 读文件非空, 字节数留痕, 打回返工, 实证落盘, 交付产物, 重试上限, 假落盘, 空文件, read 回读, LastWriteTime]
problem_patterns: ["write 工具返回成功回执但文件实际未写入，口头声称已落盘后被用户实查打回", "修订场景未实查上版产物状态就动笔，基于'记忆中的上版'修订", "交付摘要中的落盘断言无验证证据背书，下游阶段建立在空产物上"]
source_sessions: [ses_e4a8255ddffe4xkaAcVNu9UMeZ, ses_e4a6ba8f9ffecyMav4uHrFi453]
project: Date
severity: high
quality_score: 92
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
utility_score: 100
tier: S
related_experiences: ["2026-11-07-long-design-doc-chunked-write-structure-verify", "2026-11-07-subagent-delivery-spot-check-acceptance", "2026-11-06-glob-empty-result-read-verify", "2026-11-07-rejection-reasons-to-revision-actions-mapping", "2026-11-07-write-then-verify-persistence-check"]
---

# write 成功回执不等于落盘成功，交付级文件写后必须实证存在且非空

## Scenario

子智能体（spec-requirement-agent）产出需求规格并声称落盘。上一轮 v1 声称已写入 `.codeartsdoer/specs/optimization_plan/spec.md`，但该目录实测存在却为 0 文件——写入静默失败（回执仍成功），用户在资源管理器中亲自确认文件夹为空后整版打回。本轮重写后必须先证明"真的写进去了"再交付。

## Key Signals

- 上版产物目录存在但 0 文件，与"上一轮声称落盘成功"直接矛盾——工具回执与磁盘实况脱节的实证。
- 用户绕过工具链、用操作系统文件管理器核实为空——落盘真实性已被终端用户验证环节盯上。
- 下游（用户审阅、design/tasks 阶段）完全依赖产物真实存在：落盘失败会让整条流水线建立在空产物上。
- 修订场景的信号：派工单声称"上一版在目录 X"，但未实查目录就动笔有风险——上版可能根本不存在。

## Essence

工具的"写入成功"回执是执行侧声明，不是磁盘实况证明。当写入会静默失败（回执照常成功）时，唯一可信的是事后实证：列目录确认文件名列出 + 读文件确认内容非空。把"声称落盘"升级为"实证落盘"只多一次读操作的成本，却能拦住"整版交付物缺失"级事故。注意与 edit 的区别：edit 在目标文本未命中时自带报错（失败信号内置），无需逐块读回；write 的静默失败恰好相反，必须主动验证。

## Approach

1. **写后立即实证**：交付级文件每次 write 后，read 目标目录条目，确认文件名出现在目录列表中。
2. **非空验证**：read 文件确认内容可读且非空，或列目录取字节数（Length）；两者同时做即双重验证。
3. **验证输出留痕**：把验证结果（字节数/行数/LastWriteTime）写进交付摘要，作为"实证落盘"证据，供审阅者免自行核对。
4. **失败分支有上限**：验证失败（文件不存在/0 字节）→ 重写并重验，重试 ≤3 次；仍失败则显式呈报目标路径与错误信息，禁止口头声称成功。
5. **修订前实查上版状态**：修订场景先 read 目标目录，确认上版产物是否真实存在；不存在则声明"本版为全新写入"，不假装修订。

## Faster Next Time

- 交付摘要中禁止出现无实证背书的"已落盘/已写入"断言；验证句式可直接复用："列目录确认实存 + 读文件确认非空（N 字节/N 行）"。
- 成本对比：验证是秒级读操作；被打回是整版作废+用户信任损失。
- 警惕信号：用户亲自去文件管理器核对产物，说明落盘真实性已被怀疑，后续所有落盘必须带验证证据。
- 强化纪律：同一会话内只要出现过一次落盘失败（假落盘/空文件），本次任务的所有写入一律走"列目录+读文件"两步验证，不做豁免。

## Applicability Boundaries

- 适用：交付级产物（会被用户审阅或被下游阶段消费的文件），尤其是曾发生过落盘失败的目标目录；子智能体的落盘产物（结果只以总结形式返回主智能体，中间态无人复核，落盘后必须自验再返回）。
- 不适用：edit 追加写入（未命中自带报错，验证冗余，见 related 长文档条）；过程性临时文件；只读操作。
- 边界：验证只证明"存在且非空"，不证明"内容正确"——内容级正确性需另外的验收条款，本条不覆盖。
- 平台：实证于 CodeArts 码道平台 + Windows 环境（write 静默失败一例）；其他平台是否复现未验证，但"回执不可信、实证兜底"的对策平台无关。

## Evidence or Examples

- 来源会话：ses_e4a8255ddffe4xkaAcVNu9UMeZ（2026-11-07，Date 项目 optimization_plan 特性 spec 修订阶段，spec-requirement-agent 执行，6 条消息）。
- v1 事故实证：`.codeartsdoer/specs/optimization_plan/` 目录存在但 0 文件；用户打回理由之一即落盘失败；本轮动笔前 read 该目录确认 0 entries，据此声明"v1 无存量可读，本版为全新写入"。
- 本轮验证实证：write 后 bash 列目录输出 `spec.md Length: 27534 / LastWriteTime: 2026/11/7 18:13:55`，随后 read 显示 392 行非空内容——双重验证通过后才交付。
- 事故已固化：v2 规格将"任何落盘后必须读文件/列目录验证存在且非空（重试 ≤3 次，仍失败呈报路径与错误）"写成硬性需求条款（R3.x）。
- 同会话 ses_e4a6ba8f9ffecyMav4uHrFi453 复用实例：v3 重构后两步验证输出 `spec.md 52601` 字节（LastWriteTime 18:40:14）+ 回读 630 行确认头部版本/日期/编号元信息完整。合并条目"写后必验两步验证法"（2026-11-07-write-then-verify-persistence-check，已归档）的步骤与警示信号已并入本条。