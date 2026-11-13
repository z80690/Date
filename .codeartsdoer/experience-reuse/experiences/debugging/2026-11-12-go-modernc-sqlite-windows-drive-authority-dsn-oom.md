---
id: 2026-11-12-go-modernc-sqlite-windows-drive-authority-dsn-oom
title: modernc SQLite 在 Windows 报 out of memory(1)：DSN 盘符落 authority 位，DSN 逐变体探针+真实 DSN dump 对照定位
category: debugging
nature: pitfall
created_at: 2026-11-12T22:29:45
updated_at: 2026-11-12T22:29:45
tags: [SQLite, Go, Windows, DSN, 根因定位]
keywords: [modernc.org/sqlite, out of memory (1), file:// 双斜杠, 盘符 authority, url.URL DSN 构造, 探针对照, go version -m, 升级驱动无效, 只读副本修复, stdio 冒烟]
problem_patterns: [Go 程序在 Windows 打开任何 SQLite 库都报 SQL logic error: out of memory (1)，与路径权限/文件损坏无关, 升级 modernc 驱动版本后重构建仍复现同一 OOM，误判为驱动 bug 继续换版本, 手工构造探针 DSN 全部正常但目标程序仍 OOM，怀疑不到目标代码自身的 DSN 构造差异]
source_sessions: [ses_e3024c46cffeogzf8wCK8buHaO]
project: Date
severity: high
quality_score: 92
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-12-readonly-third-party-repo-copy-for-bugfix-rebuild]
---

# modernc SQLite 在 Windows 报 out of memory(1)：DSN 盘符落 authority 位，DSN 逐变体探针+真实 DSN dump 对照定位

## Scenario

Windows 上运行 Go 编译的程序（第三方框架服务端/构建端二进制），底层使用 modernc.org/sqlite 纯 Go SQLite 驱动。程序打开任意 .db 文件一律失败，报 `SQL logic error: out of memory (1)`，整条部署链被阻断。错误文本极具误导性——"out of memory" 让人先怀疑内存、权限或文件损坏，几乎不会想到是连接串形态问题。

## Key Signals

- 首个异常：`OpenSQLite C:/.../xxx.db: SQL logic error: out of memory (1)`，同一目录换路径复现。
- 误导线索（逐一排除后均非根因）：
  - 目录可写探测通过（写探针文件成功）→ 排除权限；
  - Python `sqlite3` 能读同一 .db（表结构/数据完好）→ 排除文件损坏；
  - 升级驱动 modernc v1.30.1 → v1.34.4 重构建 → 仍 OOM → 排除驱动版本；
  - CGO 重构建 → 仍 OOM → 排除纯 Go/CGO 差异。
- 决定性线索：错误串前缀含 `open readonly sqlite`——目标程序走的是 `OpenReadOnly` 路径，其内部构造的 DSN 形态与手工探针不同。
- 复现条件：DSN 为 `file://C:/...`（双斜杠）形态。`url.URL{Scheme:"file", Path:"C:/..."}.String()` 产出该形态时，盘符 `C:` 落入 URL 的 authority（Host）位，modernc 驱动对此形态报 OOM。

## Essence

根因因果链完整链：代码用 `url.URL{Scheme:"file", Path: filepath.ToSlash(abs)}` 构造 DSN → `String()` 输出 `file://C:/...`（双斜杠，盘符被当 Host）→ modernc.org/sqlite 对该 URI 解析失败并以 `out of memory (1)` 报错（错误语义与真实原因完全脱节）。正确形态是 `file:///C:/...`（三斜杠、Host 为空）或直接裸路径。驱动升级无效，因为缺陷在调用方的 DSN 构造，不在驱动版本。

## Approach

排查决策树（按序，命中即停）：

1. 先做排除验证（各 1 条命令）：目录写探针文件；用 Python/独立工具读同一 .db。两者通过则权限与文件因素出局。
2. 写最小探针程序（放进目标 module 内，复用其依赖）逐变体测 DSN：裸路径 / `file:///C:/...`（三斜杠）/ 无 pragma / 原始 DSN。**探针全部 OK 时结论是"驱动与文件都没问题，差异在目标程序的调用链"**——这是转向点。
3. dump 目标代码真实构造的 DSN：在目标 storage 层加一行 `fmt.Fprintln(os.Stderr, dsn)`（或写等价探针直接 import 其 storage 包调用 `OpenReadOnly`），与探针 DSN 对照。本例对照锁定：探针 `file:///C:/...` OK，真实 DSN `file://C:/...` OOM。
4. 用 `go version -m <exe>` 考古二进制内嵌依赖版本，确认"升级后的新 exe 确实用了新驱动"（排除构建缓存假象），此后不再在版本方向空耗。
5. 修复落位：改调用方 URL 构造保证三斜杠形态（Host 为空的 file URI 显式补第三斜杠），在只读仓库副本内修复重构建（见 related 副本修复经验），产物路径切换到副本。
6. 验证收口：stdio 冒烟——喂 JSON-RPC initialize 握手帧，断言返回合法 capabilities 且日志输出"N 个知识库加载"（N≥1），证明从 OOM 到可用全链闭合。
- 降级路径（修复暂不可得时）：从仓库 docs/ 报告目录找合法的 `.sql` dump（如既有 knowledge.sql），用 Python `sqlite3` 执行重建 .db 绕过构建管线；查询端以只读方式打开该 .db 先行可用。

## Faster Next Time

- 见到 modernc sqlite `out of memory (1)`，**第一查 DSN 形态**（Windows 盘符是否落入 authority 位：`file://C:` 即嫌疑），不要先怀疑权限/文件损坏/驱动版本。
- 探针必须复刻目标程序的真实 DSN 构造调用（直接 import 其 storage 包最精确）；手工猜 DSN 变体全 OK 反而会把自己带进死胡同——此时唯一差异只能在目标代码的构造链里。
- `go version -m <exe>` 是"验证二进制里到底编译进了什么"的一手证据，升级依赖后先考古再测行为。
- OOM 语义失真提示：modernc 驱动的报错文本不可按字面理解，`out of memory (1)` 在 Windows 场景已实证对应 URI 解析失败。

## Applicability Boundaries

- 适用：Windows + Go + modernc.org/sqlite（纯 Go 驱动）_any_ 版本（实证 v1.30.1 与 v1.34.4 均复现）；也提示其他纯 Go SQLite 驱动可能存在同类 URI 形态敏感。
- 不适用：mattn/go-sqlite3（CGO）绑定；Linux/macOS（无盘符 authority 问题）；报错确实由内存不足引发的场景（此时错误伴随明确的大结果集/内存分配上下文）。

## Evidence or Examples

- 真实 DSN dump（目标程序内）：`file://C:/Users/Administrator/Desktop/Date/temp/cairn-p003.db?_pragma=busy_timeout%285000%29&_pragma=query_only%281%29&mode=ro` → `PING-ERR: SQL logic error: out of memory (1)`。
- 探针输出：DSN1-original / DSN2-nopragma / DSN3-barepath / DSN4-urislash2 / DSN5-paren-raw / DSN6-single-pragma 全部 `OK nodes=17`（同库同驱动）。
- `go version -m` 对照：新 exe `dep modernc.org/sqlite v1.34.4`，旧 exe `v1.30.1`——升级确实生效但 OOM 不变，从而锤死调用链。
- 修复后冒烟：`Cairn MCP Server devel (multi-DB)` 握手返回合法 JSON-RPC result，日志 `1 个知识库 / 1 KBs loaded`，EXIT=0。
- 复现环境：win32 / go1.26.5 windows-amd64 / 只读第三方仓库 D:\refs\Cairn（副本 D:\refs\Cairn-build 内修复）。