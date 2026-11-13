---
id: 2026-11-12-sequential-edit-chain-one-per-turn-insert-last
title: 顺序依赖编辑链一步一轮：同轮多 Edit 并行顺序不保证 + 插入式 Edit 最后执行
category: workflow
nature: technique
created_at: 2026-11-12T17:34:44
updated_at: 2026-11-12T17:45:34
tags: [文档修订, 批量编辑, 并行工具调用, 编号顺延, SDD规格]
keywords: [Edit 并行顺序, 顺序依赖编辑链, 一步一轮, oldString 唯一性污染, 插入式编辑最后执行, 章节顺延, 同轮提交顺序, 落盘验证三件套, grep 双向校验, 大文档修订]
problem_patterns: ["编号顺延链上相邻两步同轮提交 Edit，前一步输出改变后一步的匹配环境，导致非唯一匹配或错位", "插入新章节的 Edit 与原章节标题改号同轮执行，newString 自带同名标题行污染 oldString 唯一性", "误以为同轮多 Edit 按提交顺序执行，用顺序排列替代轮次拆分"]
source_sessions: [ses_e30f06503ffeLtMm6vQXlHK2tM]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-07-renumber-revision-edit-ordering-residue-check, 2026-11-11-edit-tool-mtime-conflict-reread-resubmit, 2026-11-06-parallel-tool-call-doom-loop, 2026-11-12-supplemental-ruling-additive-revision-exception-registration]
---

# 顺序依赖编辑链一步一轮：同轮多 Edit 并行顺序不保证 + 插入式 Edit 最后执行

## Scenario

对数百行结构化 markdown 基线文档做版本修订，需在中间插入新章节并使其后所有章节编号整体顺延，全文另有密集编号交叉引用需联动改写。修订通过多次 Edit 完成，且为提速在同一轮内提交多个 Edit。规模参照：本次实战为 666→814 行规格文档 v1.0→v1.1，插入一整章 + 新增门禁编号体系 + 8 组交叉引用联动，共 13 轮编辑完成。

## Key Signals

- 关键实证：同一轮内提交的多个 Edit 是**并行执行、完成顺序不保证**的——"同批 Edit 按提交顺序排列即可安全执行"的假设不成立（本会话独立技能审查后，已据此修正既有技能文档中该口径）。
- 危险信号：顺延链上相邻两步（如 5.4.1→5.5.1 与 5.3.1→5.4.1）若同轮提交，前一步的 newString 产生的文本会成为后一步 oldString 的额外匹配源或破坏其唯一性，触发"非唯一匹配"报错，或更危险地改错位置。
- 危险信号：插入新章节的 Edit 其 newString 自带与小节标题同名的标题行（如"### 5.4.1"），若同轮还有针对原章节标题的改号 Edit，oldString 唯一性被污染。
- 痛点：顺延改完后无法肉眼确认几十处交叉引用零漏改，需结构化验证兜底。

## Essence

Edit 工具的同轮多调用是并行语义，顺序控制必须从"轮内排列"上移到"轮间拆分"：顺序依赖的编辑链一步一轮，每轮只放彼此不相邻（A 的输出不改变 B 的匹配环境）的编辑。插入式 Edit 因其 newString 引入新文本、天然改变后续匹配环境，必须放整批改号完成后的最后一轮。完成度证据不靠人工目检，靠三件套验证闭环。

## Approach

1. 动笔前把修订拆成两类：改号链（尾部倒序，方向纪律见相邻经验）+ 联动引用改写（彼此独立）。
2. 顺序依赖链上相邻两步严禁同轮：**一步一轮**；互不相邻的独立编辑可同轮并行（每轮 ≤4 个为宜，本次实测主标题与小节标题分布不同位置、匹配文本互不重叠，同轮全部一次成功）。
3. 插入新章节的 Edit 放整批改号完成后的最后一轮，**一步完成"插入新章 + 原章节主标题改号"**——先单独改号会留下旧主标题与插入 Edit 的 newString 撞唯一性。
4. 每轮 Edit 返回成功即视作该轮已并行完成，不以提交顺序推断执行顺序；失败时先读报错再重试，不盲改。
5. 收尾验证三件套：列目录（确认字节数非空）+ read 抽查关键修订区 + grep 双向校验（旧编号残留清零 + 新结构落位计数与预期吻合）。

## Faster Next Time

- 一句话纪律：**改号链一步一轮，插入最后；同轮只放互不相邻的编辑**。
- 拆轮判据：同一轮内两个 Edit 存在"A 的输出会改变 B 的匹配环境"关系（A 产生或消除 B 的 oldString 匹配源）→ 拆轮。
- ROI：本次 13 轮编辑全部一次成功、零非唯一匹配报错、零 mtime 冲突，grep 校验旧编号残留在受影响区清零、新章节标题 7 处落位——避免了"同轮相撞→报错→重读→重排"的返工循环，分钟级成本锁死几十处引用零漏改。

## Applicability Boundaries

- 适用：oldString/newString 唯一匹配类编辑工具的批量修订；编号顺延、重命名链、跨节引用联动等顺序依赖场景。
- 不适用：整文件重写（直接 write 更快）；彼此完全独立的编辑（可放心同轮并行，无须拆轮）；单 Edit 事务（天然有序）。
- 相邻经验边界：2026-11-07-renumber-revision-edit-ordering-residue-check 独有点是替换方向（从后往前保唯一）与 grep 双向核验，且其"分批执行（每批 5-6 个 Edit）"口径隐含同轮顺序可控——本条实证修正为一步一轮；两经验互补：那条管方向与验证，本条管轮次编排与插入位次。同一修订任务的策略面（例外登记双指针、暂挂标注、评估框架版防虚构）见 2026-11-12-supplemental-ruling-additive-revision-exception-registration。

## Evidence or Examples

- 来源会话：ses_e30f06503ffeLtMm6vQXlHK2tM（2026-11-12，Date 项目 P003 spec 补充前置门禁章节，spec-requirement-agent 子代理执行）。
- 实际编排：轮 4~9 倒序改号（原 5.8→5.9 起，逐章顺延），每轮内编辑互不相邻；轮 10 一步完成"插入新 5.3 前置门禁章 + 原 5.3 主标题改 5.4"；13 轮全部一次成功、零报错。
- 核验实测：grep 旧编号引用残留在受影响区清零；新章节标题 7 处、门禁编号相关引用 15 处落位符合预期；列目录确认 spec.md 70,940 字节非空。
- 独立确认：同会话后台技能审查智能体复核本模式后，将既有技能文档中"同批 Edit 按顺序排列即可安全执行"的表述修正为"同轮并行、顺序不保证、相邻两步必须分轮"，与本条结论一致。
- 证据边界：顺延链相邻两步同轮相撞为机制推理+预防性规避，本次未实际踩坑报错；失败模式可由 Edit"非唯一匹配"报错机制确认，信号明确可辨。