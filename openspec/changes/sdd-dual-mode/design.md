# Design: SDD 双模式工作流

## Context

现成 `sdd-spec-pipeline` 技能有四步契约但无机器触发；自写门禁脚本已落盘；OpenSpec CLI v2.2.0 已装已 init。产物落 `log/<日期>-<特性>/`，配置落 `.workbuddy/`，两套并行不混。

## Goals / Non-Goals

**Goals:**
- 触发表驱动模式判定，不靠我主动想起来
- 每步产物门禁 exit 可判，反馈前移
- CLI validate 补语义校验，自写门禁补结构 + 人工扫签收

**Non-Goals:**
- 不做自动放行（用户裁决）
- 不改协作公约正文
- 不动业务代码、不建定时任务

## Decisions

1. **双门禁并行**：自写门禁查结构（快），CLI validate 查语义（准），两个都过才完成。理由：单靠结构会放过内容偏差，单靠 CLI 缺快速反馈。
2. **双命中从严取 sdd**：防"查一下"当借口跳步。
3. **人工扫签收栏**：门禁脚本查出产物里有签收标记才算过——机器判不了内容质量，但能判"你扫没扫"。
4. **派工单强制门禁字段**：模板写死门禁命令 + 期望 exit + 贴输出回执，没贴不算完成。

## Risks / Trade-offs

- 门禁只查结构不查语义 → CLI validate 补，仍留人工扫
- CLI change 与 log 产物双写 → 以 log 为准，CLI change 只做校验
- 出网口径旧版残留 → 双处留痕（SOUL + rules_index）
