---
id: 2026-11-11-programmatic-atomic-json-state-rewrite
title: 流程收尾的超长 JSON 状态块改写用程序化原子替换：json.load→改键→dump 一次完成多项关联修改与校验断言
category: agent-ops
nature: technique
created_at: 2026-11-11T01:24:41
updated_at: 2026-11-11T01:24:41
tags: [edit边界, JSON状态文件, 程序化改写, 原子替换, 收尾落盘]
keywords: [json.load, json.dump, update_plan 清空, 超长块锚定, 整体 write 对比, 关联修改合并, 校验断言, progress.json, stage 状态落盘, ensure_ascii=False]
problem_patterns:
  - "流程收尾需清空超长 JSON 字段（含大段叙述文本）并批量落盘多个 stage 状态，edit 的 oldString 无法精确锚定超长块，为锚定而构造巨型 oldString 又引入跨块吞键风险"
  - "多项关联修改（清空字段+多阶段状态+顶层状态+标记校验）拆成多次 edit 逐项推进，次数多、每轮需验证、中途存在状态不一致窗口"
source_sessions: [ses_e39a9f84effeyyHLGi3D7QiW7b]
project: Date
severity: medium
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-08-edit-cross-block-boundary-swallows-json-key, 2026-11-11-dual-python-interpreter-path-contract]
---

# 流程收尾的超长 JSON 状态块改写用程序化原子替换：json.load→改键→dump 一次完成多项关联修改与校验断言

## Scenario

多阶段流程状态文件（progress/state/ledger 类，`stages` 下多个相邻 JSON 块）的收尾环节：需清空一个超长字段（如 update_plan，含完整判定叙述文本）、同时落盘多个 stage 状态与顶层状态，并顺带校验关联产物的标记完整性。通用 Agent 模式，不绑定特定平台；同收尾序列中的短锚点修改（如向某 dict 追加一个键）已用 edit 成功完成，本环节是剩余的"难锚定"部分。

## Key Signals

- **锚定失效信号**：目标修改块长达数十行且含长叙述文本（如 update_plan 的 verdict/filter_note），edit 的 oldString 需逐字覆盖整块——构造巨型 oldString 本身就是跨块吞键高危组合（见相邻 edit 经验），主 Agent 据此判定"无法用 edit 精确锚定"。
- **关联修改聚合信号**：同一文件一次收尾需改 ≥3 处且相互关联（清空 update_plan + stage_6/7 状态 + 顶层 status），拆成多次 edit 则每轮都要重新锚定并各自验证。
- **校验伴生信号**：修改完成后还需验证另一产物（WikiRetrieval.md 的起止标记、无占位符残留）——校验与修改合并为一次脚本执行可共享输入输出。

## Essence

edit 是文本级替换，锚定成本随 oldString 长度上升；对超长 JSON 块，两条常规路（巨型 oldString 的 edit、读全文后整体 write 人工重建）分别引入吞键风险与抄写失真风险。程序化改写把结构理解交给解析器：json.load 保证未触碰键原样保留，dict 赋值只动目标键，json.dump 落盘——机器保证替代人工重建。同一脚本内可合并多项关联修改与校验断言，把"改完了"从工具回执升级为断言输出（update_plan_cleared: true / final_status: completed），一次执行即收尾闭环。edit 与程序化改写的分界不是能力问题而是锚定经济性：短锚点 edit 优先，超长块/多项聚合走程序化。

## Approach

1. **触发判定**：满足任一即走程序化改写——① oldString 为超长块（含长叙述文本，锚定脆弱）；② 同一文件需一次落盘 ≥2 处关联修改；③ 修改后需附带结构/关联产物校验。三者皆否 → 维持 edit 小步推进。
2. **单文件一次性脚本**：`json.load` 读入 → 对 dict 直接赋值/置空目标键 → `json.dump(ensure_ascii=False, indent=2)` 写回（UTF-8）。禁止手工拼接 JSON 文本。
3. **合并校验断言**：同脚本内读取关联产物（如模板生成文件的起止标记），做存在性与无残留检查，将断言结果与修改结果一起 print 输出——输出即交付证据。
4. **短锚点保留 edit**：单键值对翻转、短块状态追加仍用 edit + 改后 `python -c "json.load"` 验证的既有组合，不为统一而改写。
5. **脚本内部路径按宿主解释器选形态**（见 2026-11-11-dual-python-interpreter-path-contract）：命令文件通道认 `/mnt/c`，直调短命令通道认 `C:/`，先看 traceback 路径形态再修路径。

## Faster Next Time

- 一行决策规则：收尾批量改写（超长块或 ≥2 处关联修改）→ Python 程序化改写；单点短修改 → edit + json.load 验证。
- 收尾脚本输出必须含断言结果（布尔/枚举字段），使"完成"可被后续阶段直接引用而非重新核验。
- 反模式：为超长块构造巨型 oldString（跨块吞键，且失败零告警）；整体 write 人工重建大文件（抄写失真风险随文件增大上升）；收尾修改逐项多次 edit（中途状态不一致窗口大、验证次数翻倍）。

## Applicability Boundaries

- 适用：任何 Agent 平台下多块 JSON/YAML 状态文件的流程收尾（progress/state/ledger 类）；单文件多项关联修改的合并执行。
- 不适用：修改目标可整体重新生成（直接重跑生成器更优，无需改写）；文件含注释或下游对键序/格式严格敏感（json.dump 会规范化格式，此时须保守手段）；Markdown 正文编辑（无语法边界）。
- 格式副作用注意：json.dump 规范化缩进与转义——trace 中 progress.json 无注释、下游纯解析器消费，安全；有格式契约的文件先确认再选通道。
- 证据等级：单次成功闭环；脚本前两次执行失败为路径宿主问题（已被 dual-python 经验单独收录），非本模式失败，路径修正后一次成功。

## Evidence or Examples

- 源会话 ses_e39a9f84effeyyHLGi3D7QiW7b（docgen-apply fork #1 主 Agent，Wiki 增量更新 version_token 213→347 的阶段 6.2 收尾）。
- edit 对照实证：同收尾序列中，module_tree 追加新模块 software_src 节点用 edit 成功（短锚点）；update_plan 清空判定"无法用 edit 精确锚定 oldString"，改走程序化。
- 程序化改写实证：收尾脚本一次执行输出 `{"wiki_retrieval_marks": {"start": true, "end": true, "placeholder_residue": false}, "update_plan_cleared": true, "final_status": "completed"}`——update_plan 清空 + stage_6/7 状态落盘 + 顶层 status 置 completed + WikiRetrieval 标记校验，四件事一次完成。
- 失败归因隔离：脚本前两次执行 FileNotFoundError 系内部 `/mnt/c` 路径被 Windows Python 解析（见 2026-11-11-dual-python-interpreter-path-contract），与本模式正交。