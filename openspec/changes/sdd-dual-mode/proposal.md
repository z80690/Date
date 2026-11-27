# Proposal: SDD 双模式工作流

## Why

规矩里写了"编码强制 SDD 四步"，但没有触发表和机器门禁，靠我主动想起来——等于没落地。人机协作反复拉扯的根因是反馈滞后、奖励信号模糊（2026-11-26 李永乐视频讨论结论）。

## What Changes

- 新增触发表 `sdd_modes.json` + 模式判定脚本 + 产物门禁脚本（已落盘并自检通过）
- 出网限制收窄：只管攻防/黑白客演练，其他任务正常出网（用户 2026-11-26 纠正）
- 安装并配置 OpenSpec CLI v2.2.0，打通 proposal→specs→design→tasks→validate→archive 链路
- 派工单模板强制门禁命令 + 期望 exit，自检脚本加"内容偏差人工扫"签收栏

## Capabilities

### New Capabilities

- `sdd-dual-mode`: 按任务类型自动分流到规范驱动（默认）或 Web Coding（例外），每步产物有可判门禁，出网口径按场景收窄。

### Modified Capabilities

无（项目此前无已归档 capability）。

## Impact

- 配置：`.workbuddy/config/sdd_modes.json`、`openspec/config.yaml`
- 脚本：`.workbuddy/scripts/sdd_mode_gate.py`、`sdd_artifact_gate.py`
- 规则：`SOUL.md` 第 53 行、`rules_index.json` S1-6
- 产物：`log/2026-11-26-sdd-dual-mode/` 下 spec/design/三报告
