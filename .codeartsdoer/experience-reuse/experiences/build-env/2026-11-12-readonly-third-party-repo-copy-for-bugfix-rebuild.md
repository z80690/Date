---
id: 2026-11-12-readonly-third-party-repo-copy-for-bugfix-rebuild
title: 第三方只读参考仓库的缺陷修复走副本：robocopy 复制→副本改源码重构建→产物指向副本，原仓库零改动
category: build-env
nature: technique
created_at: 2026-11-12T22:29:45
updated_at: 2026-11-12T22:39:19
tags: [第三方仓库, 只读约束, 副本修复, 重构建, MCP 注册]
keywords: [robocopy /XD .git, 副本目录, go get 升级, 源码修复, bin 产物切换, 原仓库零改动, 上游回馈, 修改点清单, mcp_settings command, 版本锚定]
problem_patterns: [第三方参考仓库存在平台兼容 bug 不修就无法用，但仓库是只读隔离资产被约束禁改, 在"等上游修复"与"违规直改原仓库"之间二选一，主线任务被阻断, 修复后不知道如何既保留原仓库证据链又让下游用到修复版二进制]
source_sessions: [ses_e3024c46cffeogzf8wCK8buHaO]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-12-go-modernc-sqlite-windows-drive-authority-dsn-oom, 2026-11-06-reference-repo-isolation-nesting-prevention, 2026-11-11-third-party-repo-clone-vetting-not-a-module]
---

# 第三方只读参考仓库的缺陷修复走副本：robocopy 复制→副本改源码重构建→产物指向副本，原仓库零改动

## Scenario

外部参考仓库按惯例隔离存放于项目外只读目录（如 `D:\refs\<Repo>`），作版本锚定的引用资产。实测发现其实质缺陷（本机平台兼容 bug），不修复则下游部署/注册链全部阻断；而"不删文件、不改第三方源码"类红线禁止直改原仓库。需要一条既保住原仓库证据链、又让修复版可用的落位方式。

## Key Signals

- 原仓库 HEAD 是既定锚点（pre_check/留痕文件引用 `git rev-parse HEAD` 值），直改会破坏证据链。
- 复制成本极低：955 文件 / 193MB，robocopy 秒级完成——"修复成本"不应成为直改原仓库的理由。
- 修复涉及两层改动：依赖升级（`go get`）+ 源码修改（Edit），都会产生大量工作区变更。

## Essence

把"只读约束"与"可用性需求"解耦：修复动作全部发生在姊妹副本目录内，原仓库保持只读零改动；下游注册与引用一律指向副本产物。副本与原仓库的版本关系（同一 HEAD 起点 + 修改点清单）留痕，具备向上游回馈的完整证据。

## Approach

1. 复制副本（排除 .git 控制体积）：`robocopy D:\refs\<Repo> D:\refs\<Repo>-build /E /XD .git`；PS5.1 下 robocopy exit code 1 = 正常复制成功（非错误），勿按 $LASTEXITCODE 0 判定。
2. 副本内执行依赖与源码修改：`go get <dep>@<version>` 升级驱动；Edit 修复缺陷点（修复点先经探针/DSN 对照锤死根因再动笔）。
3. 副本内重构建目标产物：`go build -o bin/<name>.exe ./<cmd-path>`；构建成功以产物存在 + 尺寸合理为准，忽略无 module 上下文的 LSP 误报。
4. 下游切换产物指向：注册配置（如 mcp_settings.json 的 `command`）写副本产物**绝对路径**；写前备份原配置，写后做解析+路径存在性+结构三验。
5. 冒烟验证：对产物做最小功能探针（如 stdio 握手帧 + 资源加载数输出），断言缺陷消失。
6. 留痕三件：副本起点 HEAD 与原仓库一致；修改点清单（文件:行 + 根因指针）；"可回馈上游"备注（issue 素材已成形）。

## Faster Next Time

- 发现第三方仓库 bug 且本机无 PR 回馈通道时，直接走副本修复，不要在"等上游"与"违规改原仓"之间卡死主线。
- 预判成本先测体积（`Get-ChildItem -Recurse | Measure-Object` 求和），百 MB 级以下复制是秒级操作，不构成直改原仓库的理由。
- 修改前先在副本内做一次基线构建/冒烟，确认缺陷在副本可复现——排除"复制过程引入差异"的干扰变量。
- 注册配置写完当轮只做静态三验，运行时可见性留给新会话重载（本地二进制 MCP 注册的既有分层验证契约）。

## Applicability Boundaries

- 适用：本地克隆/参考类仓库（隔离目录存放、无需贡献 git 历史）；体积可接受复制；缺陷修复以二进制产物交付（MCP server/CLI 工具类）。
- 不适用：需要保持 git 历史连续以提交 PR 的场景（此时应走 fork 分支）；原仓库本身就在活跃开发且修复会被拉取覆盖的场景（副本会过期，须登记重同步触发条件）。

## Evidence or Examples

- 实测：`robocopy D:\refs\Cairn D:\refs\Cairn-build /E /XD .git` → ROBOCOPY_EXIT=1（复制成功）；`FILES=955 SIZE=193.5MB`。
- 修复链：副本内 `go get modernc.org/sqlite@v1.34.4`（go.mod 确认 upgraded v1.30.1 => v1.34.4）→ Edit `core/storage/sqlite.go` 的 DSN 构造（盘符 authority 位修复）→ `go build` 产出 `bin/cairn-mcp.exe`（17,012,720 B）。
- 下游切换：mcp_settings.json `command=D:\refs\Cairn-build\bin\cairn-mcp.exe`（写前备份 mcp_settings.json；PARSE=OK / CMD_EXISTS=True / ENV_COUNT=0 三验过）。
- 冒烟：stdio 握手返回合法 result 且 `1 KBs loaded`——原仓库同 HEAD 零改动，可回馈上游的修改点已留痕。