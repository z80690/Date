# Spec Delta: sdd-dual-mode

## Purpose

按任务类型分流到规范驱动或快速通道，让每阶段产物有机器可判的门禁，把反馈从"干完才说不对"前移到"每步验"。

## ADDED Requirements

### Requirement: 模式自动判定

任务进入时系统 SHALL 按触发表判定模式：命中写代码/开发/重构等关键词取 sdd（exit 0），只命中查一下/核对/实验等取 web-coding（exit 1），双命中取 sdd，零命中输出 need-clarify（exit 2）并问用户。

#### Scenario: 编码任务

- **WHEN** 任务描述为"写代码"
- **THEN** 判定 sdd，exit 0

#### Scenario: 核对任务

- **WHEN** 任务描述为"核对一下规则"
- **THEN** 判定 web-coding，exit 1

#### Scenario: 零命中

- **WHEN** 任务描述两类关键词都不命中
- **THEN** 输出 need-clarify，exit 2，不自行选模式

### Requirement: 产物门禁

每阶段产物落盘后系统 SHALL 校验文件存在、非空、必填章节齐、字数达标，并附"内容偏差人工扫"签收栏；exit 0 才可呈报用户，非 0 当场补。

#### Scenario: 门禁通过

- **WHEN** design.md 章节齐、字数达标且人工扫签收栏已填
- **THEN** exit 0，允许呈报

#### Scenario: 门禁失败

- **WHEN** 产物缺必填章节
- **THEN** exit 1，列出缺项，不放行

### Requirement: 出网口径按场景收窄

攻防/黑白客演练 SHALL NOT 碰外部真实目标，只走 127.0.0.1；其他任务 SHALL 正常出网不需逐次报备。

#### Scenario: 普通装包

- **WHEN** 任务是 npm 安装依赖
- **THEN** 允许正常出网

#### Scenario: 攻防演练

- **WHEN** 任务是黑白客攻防测试
- **THEN** 禁外部目标，只走本机回环靶机

### Requirement: 逐步门禁

需求、设计、任务三份产物 SHALL 逐份呈报、逐份等用户确认；不得一次性生成。用户只对需求做主评审，设计/任务只偶发纠偏。

#### Scenario: 需求确认后进设计

- **WHEN** 用户确认需求规格
- **THEN** 才生成 design.md
