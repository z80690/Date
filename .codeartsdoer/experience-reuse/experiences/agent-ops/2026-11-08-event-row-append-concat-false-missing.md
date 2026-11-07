---
id: 2026-11-08-event-row-append-concat-false-missing
title: 表格事件行 Edit 追加可能以 || 拼接生效，截断式抽查会把"已写入"误判为"缺失"
category: agent-ops
nature: pitfall
created_at: 2026-11-08T01:22:36
updated_at: 2026-11-08T01:47:04
tags: [事件流水, edit追加, 行拼接, 截断抽查, 假缺失, 留痕验证]
keywords: [事件流水, 表格追加, 换行失效, 行拼接, tail截断, 假缺失, 复验注, 拆行修复, 子代理留痕, 全行重读]
problem_patterns: ["子代理声称已向表格追加事件行但验证时看不到，误判缺失后补写造成重复", "edit 追加新行实际拼接在上一行行尾，留痕结构损坏且难以察觉", "用 tail 或固定长度截断验证长表格行存在性，行尾内容被截掉导致误判"]
source_sessions: [ses_e4901eb75ffel23pcFPtONtVPN]
project: Date
severity: medium
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-06-edit-conflict-reread-then-reapply, 2026-11-07-write-receipt-not-proof-of-persistence, 2026-11-07-subagent-delivery-spot-check-acceptance, agent-ops/2026-11-08-marker-format-drift-regex-count]
---

# 表格事件行 Edit 追加可能以 || 拼接生效，截断式抽查会把"已写入"误判为"缺失"

## Scenario

多智能体协作流程用 Markdown 表格文件做事件流水（每事件一行，含轮次/时间戳/发布方/产物指针），由主智能体与子智能体交替追加行；追加后需要验证"新行是否已写入"。常见验证动作用 bash `tail -1` 或固定长度截断（如 `Substring(0,160)`）抽查文件尾部。

## Key Signals

- 子代理返回摘要声称"已追加为独立行"，但主智能体用 tail/截断检查看不到该行内容——疑似未写入。
- 对同一文件 edit 追加时报 "File has been modified since it was last read"（Last modification 晚于 Last read），重读后发现"缺失"的行其实已存在。
- 文件总行数比事件数预期少 1——两行内容挤在同一物理行内。

## Essence

两层复合陷阱叠加：

1. **追加生效形态缺陷**：Edit 向表格追加新行时，实际生效形态可能是把新行以 `||` 拼接在上一行行尾（未真正换行），主/子智能体侧均复现——写入成功但行结构不合规。
2. **截断式抽查假缺失**：tail/固定长度截断只显示行首，行尾拼接内容被截掉，形成"假缺失"——行已写入却被判定缺失；若按缺失去补写，同一事件二次污染。

验证存在性必须读全行，验证格式合规性必须看换行边界；两者缺一就会把"格式不合规的成功写入"误判为"彻底没写入"。

## Approach

1. 追加表格行前：先重读目标文件最新内容（刷新 edit 基线 + 确认末行锚点原文）。
2. 追加后立即重读该文件，检查新事件是否占独立行（前一行末尾不应出现 `||` 直连新事件名）。
3. 存在性验证禁用 tail/固定长度截断判定；用整行读取，或用正则对全文件逐行计数（如 `^\| E\d` 类行首模式计数）。
4. 发现拼接：拆行修复（以拼接段原文为 oldString、换行为 newString，内容零改动），补"复验注"留痕说明修复动作，再重读确认一次。
5. 子代理侧执行追加时，把"追加后重读确认独立行"写进其 SOP；主智能体收到"已追加"声明后按同一标准复验，不复述子代理结论。

## Faster Next Time

- 一句话纪律：**"声称追加 ≠ 独立成行；追加后重读全行，禁 tail 截断判存在。"**
- "疑似缺失"的处理顺序：先整行重读确认真缺失，再考虑补写——tail 看不到 ≠ 没写入。
- 拆行修复是幂等可重放的：oldString 用拼接段原文，失败（mtime 冲突）时重读后重放即可，无需重新设计编辑。
- 同工具同文件类型"上次追加正常"不能豁免本次复验——拼接属不稳定复现缺陷。

## Applicability Boundaries

- 适用：任何以 Markdown 表格/行结构做追加式留痕的文件（事件流水、变更日志、检查清单勾选行），且写入方含子智能体或需事后验证的场景。
- 不适用：整文件一次性 write（无追加行为，改走"列目录+读非空"验证）；正文段落式追加（无行边界语义）。
- 平台：实证于 CodeArts 码道平台 Edit 工具 + Windows 环境；`||` 拼接属工具追加行为缺陷，其他编辑工具是否复现未验证，但"读全行再判定"的验证纪律平台无关。
- 与相邻经验分工：mtime 冲突的重读重放见 2026-11-06-edit-conflict-reread-then-reapply；write 级落盘验证见 2026-11-07-write-receipt-not-proof-of-persistence——本条聚焦行级追加的格式合规与"假缺失"误判，不重复上述内容。

## Evidence or Examples

- V1 轮事件流水三处复现（同一文件同一会话）：S1 出题官追加 E2 行实际拼接在 E1 行尾（主智能体 tail 误判缺失 → edit 报 mtime 冲突 → 重读发现 E2 已在，实为拼接）；主智能体随后追加 E3 行同样拼接在 E2 行尾；批改官追加 E4 行曾拼接、自行拆行修复后复验通过。
- 修复实证：以拼接行原文为 oldString 拆行重放，内容零改动，四事件 E1→E2→E3→E4 各占独立行后链路复核完整。
- 对照组：R1 轮同一主智能体逐行追加均正常成行——同工具同文件类型仍可能成功，属不稳定复现，不能凭历史成功豁免复验。