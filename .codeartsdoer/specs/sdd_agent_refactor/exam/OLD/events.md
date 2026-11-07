# 事件流水（OLD 轮——对比测试旧逻辑轮）——事件直连派工留痕

> 过程层载体：只记事实不写门禁结论；六字段=事件名/轮次标识/时间戳/发布方/接收方/产物指针。
> 本轮 trigger=COMPARE_OLD（tasks 6.2，M5 对比门）：旧版配置（git HEAD=2861cd2 检出至 temp/compare/，验证态运行，不动现行文件）按旧版五段 SOP 执行。
> 口径统一四要素（R0-7，两轮共用）：①同材料=已三查 SDD 官方文档+学习成果 ②同题量=50 题、5 角度×10 题 ③同判分规则=PASS/PARTIAL/FAIL→同一置信度公式（Σ题分/50，PASS=1/PARTIAL=0.5/FAIL=0）④同合格线呈现口径=80% 参照线。
> 独立性保障：出题不知批改结果、批改不知出题倾向与另一轮任何信息、两轮间无协商通道。

| 事件名 | 轮次标识 | 时间戳 | 发布方 | 接收方 | 产物指针 |
|--------|---------|--------|--------|--------|---------|
| E1 exam.issue | OLD | 2026-11-08 | 主智能体（trigger=COMPARE_OLD） | S1 出题官（旧版 v1 配置，temp/compare/examiner.md 验证态） | 载荷：roundId=OLD；trigger=COMPARE_OLD；domain=sdd；total=50；levels=记忆/理解/应用；angles=5角度×10题（SDD总纲/建需求/建设计/建任务/执行）；材料=`learn/materials.md`+`learn/self-evidence/sources/`（同 R1/V1 已三查材料）；落盘目录=`exam/OLD/`；SOP 版本=v1 五段（HEAD 2861cd2）。投递序：本行留痕先于派工动作 || E2' exam.issue.done（代记） | OLD | 2026-11-08 | 主智能体代记（S1 旧版 v1 无出题完成事件步骤——旧逻辑行为差异，如实留痕） | 主智能体 | 产物：`exam/OLD/questions.md`（7527B，`^\d+\.` 计数=50，三级=记忆18/理解17/应用15 三级非零）+`exam/OLD/key.md`（17401B，逐题对应，仅交付主智能体）。出题官按旧版五段 SOP ①读材料②按角度各出 10 题③key 单独成文件④交付+出题说明，完成判据自检通过（返回摘要）。无新版的 M1 门禁自检步骤（旧版无此要求，口径如实） |
| E3 answer.complete | OLD | 2026-11-08 | 主智能体 | S2 批改官（旧版 v1 配置，temp/compare/grader.md 验证态） | 载荷：roundId=OLD；answersFile=`exam/OLD/answers.md`（8734B，`^\d+\.` 计数=50，归档先于本行）。批改包三件=questions.md+key.md+answers.md。投递序：本行留痕先于派工动作 || ROUND-CANCELLED | OLD | 2026-11-08 | 用户强硬指令 U6-4（取消 OLD/NEW 对比） | —— | S2 批改派工被中止（未出分）；OLD 轮就此取消不做批改；E1/E2' 同行拼接为子代理追加换行缺陷（主智能体不再修复，如实留痕）；temp/compare/ 旧版副本随 M5 取消保留备查，M7 后清理。以 spec v5+SPEC_OPTIMIZATION.md 为准 |