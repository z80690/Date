---
id: 2026-11-06-skill-doc-env-mismatch-fallback
title: skill 文档指令与运行时环境不符时的降级执行法
category: agent-ops
nature: technique
created_at: 2026-11-06T19:29:49
updated_at: 2026-11-06T19:45:16
tags: [skill执行, 降级策略, CLI兼容, 环境探测, 码道]
keywords: [子skill, not found, unrecognized arguments, SKILL.md, 缓存目录, cb repo-doc, -h, 参数校验, 直读文档, 最小降级]
problem_patterns: [主skill引用的子skill经Skill工具加载报not found, skill文档给出的CLI参数被当前版本拒绝unrecognized arguments, 照文档执行遇环境不匹配时不知如何降级]
source_sessions: [ses_e4f7ba4bdffe5nL8JFlcchwE9L]
project: Date
severity: medium
quality_score: 85
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-06-project-knowledge-provenance-format, 2026-11-06-codeartsdoer-skill-market-registry]
---

# skill 文档指令与运行时环境不符时的降级执行法

## Scenario

按主 skill 执行多阶段流水线时，文档指令与实际运行环境出现两类不匹配：主 skill 引用的子 skill 无法经 Skill 工具加载；skill 文档给出的 CLI 命令含当前版本不支持的参数。此时若中止流程或盲目重试，都会浪费整轮执行。

## Key Signals

1. Skill 工具返回 `error: Skill "<主skill>:<子skill>" not found`——子 skill 只落盘为文档，不注册为独立可加载技能。
2. CLI 返回 `error: unrecognized arguments: <参数名>`——skill 文档中的参数被本地安装版本拒绝，属版本演进差异，非命令拼错。

## Essence

skill/子 skill 文档是执行意图说明，不是运行时契约。子 skill 通常不进入技能注册表；CLI 参数集随版本增减。正确动作是"探测环境 + 最小降级"：保留流程结构与产物格式不变，只替换不兼容的加载方式或参数子集。

## Approach

1. 子 skill 加载报 not found → 立即 glob 主 skill 安装缓存目录：`<用户目录>/.codeartsdoer/cache/system/skills/<主skill>/skills/*/SKILL.md`，直接读取对应子 skill 文档并按其规则执行，与 Skill 工具加载等效。
2. CLI 参数不被识别 → 立即执行 `<命令> -h` 查看当前版本实际参数集，按可用子集执行：保留语义等价的参数（如文档要 `--skip-cards --skip-heavy-extraction`，实际只支持前者则只传前者），丢弃不存在的参数，不改流程结构。
3. 降级后仍按原 skill 的阶段顺序与校验动作推进，保证产物与进度文件的格式、路径完全一致，不影响断点续传。

## Faster Next Time

- 主 skill 启动前先 glob 一次缓存目录，预知哪些子 skill 需要走"文档直读"路径，省掉一次报错往返。
- skill 文档中的任何 CLI 命令首次执行前先 `-h` 校验参数存在性，一次避免"报错→查帮助→重试"三步。
- 警告信号：报错含 `not found` / `unrecognized arguments` 时，优先怀疑"文档 vs 环境差异"，而不是怀疑自身流程写错。

## Applicability Boundaries

- 适用：主 skill 已在环境中激活、其子 skill 文档落盘于缓存目录结构（观察于码道 CodeArts Agent 的 `.codeartsdoer/cache/system/skills/`）；模式本身是通用 Agent 模式。
- 不适用：子 skill 文档在缓存目录中根本不存在（应中止并记录，不得凭猜测补写流程）；CLI 缺失的参数承载核心功能（应停止而非降级硬跑）。

## Evidence or Examples

- `skill(repo-simple-wiki:stage0-mode-detection)` → `error: Skill "repo-simple-wiki:stage0-mode-detection" not found`；改直读 `C:\Users\Administrator\.codeartsdoer\cache\system\skills\repo-simple-wiki\skills\stage0-mode-detection\SKILL.md` 后，阶段 0 按文档规则正常执行。
- `cb repo-doc <dir> --language zh --skip-cards --skip-heavy-extraction` → `error: unrecognized arguments: --skip-heavy-extraction`（cb 0.2.62）；`cb repo-doc -h` 确认支持 `--skip-cards`，按参数子集执行后成功产出全部 scan 产物（endpoints/imports/pkg_deps/clients/summary/architecture/symbols 齐全）。