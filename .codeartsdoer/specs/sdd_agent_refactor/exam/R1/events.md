# 事件流水（R1 轮）——事件直连派工留痕

> 过程层载体（design §2.1.3-5-4）：只记事实不写门禁结论；六字段=事件名/轮次标识/时间戳/发布方/接收方/产物指针。
> 去重键=roundId+事件名；同一轮次同一事件名重复→忽略动作但留痕"重复命中"。

| 事件名 | 轮次标识 | 时间戳 | 发布方 | 接收方 | 产物指针 |
|--------|---------|--------|--------|--------|---------|
| E1 exam.issue | R1 | 2026-11-07 | 主智能体（trigger=M1_PASS） | S1 出题官 | 载荷：roundId=R1；trigger=M1_PASS；domain=sdd；total=50；levels=记忆/理解/应用；angles=5角度×10题（SDD总纲/建需求/建设计/建任务/执行）；evidenceRef=`gates/m1-learn-gate.md`；材料=`learn/materials.md`+`learn/self-evidence/sources/`（已三查）。期望产物：`exam/R1/questions.md`+`exam/R1/key.md`。投递序：本行留痕先于派工动作（H3+流水先记行） || E2 exam.issue.done | R1 | 2026-11-07 | S1 出题官 | 主智能体 | 产物：`exam/R1/questions.md`（7970B，50 题连续）+`exam/R1/key.md`（18918B，逐题对应，仅交付主智能体）。自检结论：题数=50（`^\d+\.（` 计数实证）、三级覆盖=记忆20/理解19/应用11、题答分离声明在档；主智能体复验=列目录+读文件+UTF8 双确认，key 抽验（题1–4/50）与题目对应正确。S1 完成即退，无后续主动动作 || E3 answer.complete | R1 | 2026-11-07 | 主智能体 | S2 批改官 | 载荷：roundId=R1；answersFile=`exam/R1/answers.md`（13874B，50 题计数实证，归档落盘晚于 E2 核验）。归档为硬前置已满足后发布本行（先流水记行后派工 S2）。批改包三件=questions.md+key.md+answers.md || E4 grade.complete | R1 | 2026-11-07 | S2 批改官 | 主智能体 | 产物：`exam/R1/review-report.md`（7445B，逐题判定表 50 行实证 PASS48/PARTIAL2/FAIL0，综合自信度 98%=(48×1+2×0.5)/50，门禁结论=放行，独立性声明 5 条在档）。S2 完成即退。M2 门禁判定证据=`gates/m2-exam-gate.md`（本事件后由主智能体写入，判定文件回指本行——两层留痕反向互证锚点）；H7 语义：置信度刷新事实表特性进度区 |