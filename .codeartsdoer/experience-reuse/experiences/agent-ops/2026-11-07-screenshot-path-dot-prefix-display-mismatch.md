---
id: 2026-11-07-screenshot-path-dot-prefix-display-mismatch
title: 用户截图指认的落点路径与磁盘实名不符：点前缀目录显示层吞点，双候选 Test-Path 实测定落点
category: agent-ops
nature: pitfall
created_at: 2026-11-07T18:31:30
updated_at: 2026-11-07T18:51:27
tags: [用户交互, 路径核实, Windows, 点前缀目录, 截图落点]
keywords: [用户截图, 前导点, 隐藏目录显示, 路径显示失真, Test-Path, 资源管理器面包屑, 落点核实, 双路径实测, 禁反问, 落错位置]
problem_patterns: [用户发截图指定产出落点，截图中的文件夹名与磁盘实际路径不一致（点前缀目录在资源管理器显示层被吞掉前导点）, 按截图字面路径创建或查找目录后落错位置、或误判"文件夹不存在", 禁反问约束下无法直接问用户真实路径，不知道如何低成本核实]
source_sessions: [ses_e4a7f3b4fffeEnN4ZZDzeCjyLV]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
utility_score: 100
tier: S
related_experiences: [2026-11-06-attachment-reference-unreachable-degrade, 2026-11-06-glob-empty-result-read-verify, 2026-11-07-write-receipt-not-proof-of-persistence]
---

# 用户截图指认的落点路径与磁盘实名不符：点前缀目录显示层吞点，双候选 Test-Path 实测定落点

## Scenario

用户以截图指认产出落点（"计划就放在这个文件夹里"），截图来自 Windows 资源管理器。地址栏/面包屑把点前缀目录 `.codeartsdoer` 显示为 `codeartsdoer`（前导点不可见）。Agent 若按截图字面拼接路径（如 `C:\Users\<user>\codeartsdoer\specs\...`）会指向不存在的位置：要么落错盘错目录，要么误判"用户说的文件夹不存在"。

## Key Signals

- 用户强调"就放在这个文件夹里"，但截图中的可见路径段与项目实际目录树对不上
- 项目真实结构含多个点前缀目录（`.codeartsdoer/`、`.obsidian/`、`.workbuddy/`），截图可见名缺前导点
- 用户截图同时表达了对上一轮落点的不满（文件夹实为空），说明落点正确性需要主动实证而非继承声称

## Essence

显示层（资源管理器面包屑等视图）对点前缀目录的渲染会吞掉前导点：用户引用的是"所见名"，磁盘存的是"实名"，二者在点前缀目录上必然分叉。不能把用户可见名当作磁盘路径的规范形式，也不能因字面路径 Test-Path 失败就断定目录不存在——先穷举显示变体（带点/不带点）再下结论。

## Approach

1. 从截图提取用户指认的文件夹名与父目录序列（只作线索，不作路径规范形式）
2. 生成双候选：`<字面名>` 与 `.<字面名>`，在项目根/用户目录两处探测
3. 单命令批量断言：`Test-Path "C:\...\codeartsdoer"; Test-Path "C:\...\.codeartsdoer"`，一次拿全布尔结论
4. 以 True 的路径为真实落点；向用户复述时使用带点的完整磁盘路径，并说明截图显示差异（结论前置）
5. 双 False 时降级：read 父目录枚举近似名再映射，不要按字面新建目录（避免制造第二事实源）

## Faster Next Time

- 用户引用任何截图/口述给出的落点时，默认"显示名≠磁盘名"假设，先 Test-Path 再动笔
- 高频点前缀目录清单（`.codeartsdoer`、`.obsidian`、`.git` 等）预先记位，截图名命中即映射
- 避免：按截图字面建新目录；反问用户"你说的是哪个文件夹"（违反禁反问偏好，且实测成本秒级远低于反问）

## Applicability Boundaries

- 适用：Windows 资源管理器视图/截图 + 点前缀目录；任何"用户可见路径"与 Agent 侧磁盘路径需对齐的场景
- 不适用：用户直接粘贴可解析的完整文本路径（文本不经历显示层，无此失真）；Linux/macOS 终端路径
- 其他操作系统（如 Finder 对点开头文件的处理）未实证，边界待验证

## Evidence or Examples

- 2026-11-07 会话实测：`---不带点目录--- False` / `---带点目录--- True`（Test-Path 双探测，同一轮输出）
- 该项目事实表印证 `.codeartsdoer` 为实名，specs 产物实际落点在其下
- 同场合并发教训：上一轮声称落盘该目录的 spec 实为空文件——落点核实与落盘验证（列目录+读文件）必须同时做，见 related `2026-11-07-write-receipt-not-proof-of-persistence`