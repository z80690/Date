# Date 项目 · WorkBuddy 工作规则（AGENTS.md）

> 本文件是 WorkBuddy 侧的**唯一规则入口**，2026-11-15 改为自包含。
> 规则全文已完整落到本目录 `.workbuddy/rules/`，WorkBuddy 运行时只读这里，不依赖码道目录。
> 建立：2026-11-15　修订：2026-11-15（补齐全文 + 功能隔离）

## 0. 功能隔离（WorkBuddy ≠ 码道）

两套工具各管各的目录，运行时互不读写、互不依赖：

| 工具 | 配置目录 | 本智能体权限 |
|---|---|---|
| WorkBuddy | `.workbuddy/` | 读写（规则/技能/子智能体/记忆都在此） |
| 码道 CodeArts | `.codeartsdoer/` | **不写、不依赖、不引用为运行时规则** |

- WorkBuddy 的规则全文在 `.workbuddy/rules/`，自包含。
- `.codeartsdoer/` 仅作历史资料，WorkBuddy 干活不读取、不加载、不挂载。
- 禁止把码道目录路径写进任何 WorkBuddy 运行时规则/技能/子智能体作为依赖。

## 1. 规则全文（WorkBuddy 侧权威源 = `.workbuddy/rules/`）

| 规则集 | 全文文件（唯一权威） | 复用来源（仅标注，非依赖） |
|---|---|---|
| 码道六条公约 | `.workbuddy/rules/项目协作公约.md` | 原 `.codeartsdoer/rule/项目协作公约.mdc` |
| 欧工八条 SOP | `.workbuddy/rules/项目工作规则.md` | 原项目根 `AGENTS` / `CLAUDE` |

**全文已完整复用，不是摘要。** 要改规则，只改 `.workbuddy/rules/` 下对应文件。
来源文件保持原样不动，仅作出处标注；WorkBuddy 运行时不读取来源文件。

## 2. 六条公约（全文见 rules）

完整六条见 `.workbuddy/rules/项目协作公约.md`。要点：全程 SDD、学习材料、仓库只读隔离、规矩层冻结、执行节制、单一事实源。

## 3. WorkBuddy 侧专用能力

### 3.1 子智能体（subagent）
`.workbuddy/agents/`，主智能体按 description 判定派工：

| 子智能体 | 角色 | 触发时机 |
|---|---|---|
| `sdd-examiner.md` | S1 出题官 | M1 放行后考核 / 重学重考 / 可运行验证 / 对比测试 |
| `sdd-grader.md` | S2 批改官 | 主智能体完成一轮 50 题作答归档后 |

### 3.2 SDD 技能
`.workbuddy/skills/sdd-spec-pipeline/SKILL.md`：spec → design → tasks → apply 四阶段，含门禁、并行双写预防、事件流水、考核闭环。用户要求"按 SDD 走/进入下一阶段"时加载。

### 3.3 规则目录
`.workbuddy/rules/` 存放 WorkBuddy 项目级规则全文，已落地 2 份（六条公约 + 八条 SOP）。

## 4. 生效说明

子智能体/技能是启动时扫描注册的。是否生效以重启后"新建对话 → Agent / 技能选择框"实测为准，本文件不声称已验证。
