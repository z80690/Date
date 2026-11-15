---
id: 2026-11-14-dispatch-fact-baseline-verification-dependency-multi-source
title: 预填事实基线实测核验与依赖清点多源交叉判定
category: workflow
nature: methodology
created_at: 2026-11-14T11:15:20
updated_at: 2026-11-14T11:18:16
tags: [fact-verification, dependency-audit, dispatch-baseline, cross-validation, knowledge-doc]
keywords: [预填事实核验, glob 重定位, 依赖清点, 声明与安装分离, vendored 内嵌依赖, imports.json, 静态扫描盲区, 一次性脚本依赖, 知识污染, 定位读取佐证]
problem_patterns:
  - "派工单预填事实与仓库实际不符，照抄导致错误结论写入规范文档"
  - "静态包管理扫描漏判：声明未安装的依赖与 vendored 内嵌源码均绕过清点"
source_sessions: [ses_e2d37b633ffeszVlcvSqEOzDa1]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences:
  - workflow/2026-11-07-sdd-spec-stage-fact-verification-and-scope-bounding
  - agent-ops/2026-11-13-lsp-diagnostics-path-attribution-triage
  - workflow/2026-11-11-repo-form-fact-drift-minimal-patch-s1
---

# 预填事实基线实测核验与依赖清点多源交叉判定

## Scenario
以执行者形态领取派工单生成项目规范/知识文档（本例为依赖管理规范），派工单内嵌"仓库事实起点"清单及扫描产物路径。工作流上下文：单智能体小任务、产物有粒度上限与结构模板约束；预填基线由上游扫描/先前会话汇总，与仓库当前实际可能已漂移。核验中发现多处预填事实失真，若直接照抄会把错误写进正式知识库。

## Key Signals
1. 按预填路径 glob 定位返回 No files found；同路径 Get-Content 报 ObjectNotFound——两条独立信号同时指向"预填路径失真"，而非偶发不可达。
2. 证据源自相矛盾：静态清点产物 pkg_deps.json 计 0 条，但已知某模块的清单文件存在 require 声明——单一来源计数不能当结论。
3. 预填的模块位置与实际目录层级不符（目录迁移/归拢后基线未同步）。

## Essence
预填事实基线只是待核验假设，不是事实；文档落笔前必须逐条实测。依赖清点的五个状态互相独立，缺一即漏判：**声明**（清单文件 require 字段）≠ **安装**（vendor/lock 目录配套存在）≠ **使用**（import 面）≠ **内嵌**（vendored 源码，不经包管理器）≠ **临时**（一次性脚本依赖，不属于正式依赖）。静态扫描产物只作线索不作结论。

## Approach
1. 对派工单每条预填事实执行"定位→读取→佐证"三步：先按预填路径定位；成功后读文件头/关键字段确认内容；再用第二来源佐证（如 import 面清单、目录罗列、原始清单文件）。
2. 路径定位失败立即换策略：按文件名全仓库 glob 重定位（如 `**/<文件名>`），一次命中即修正路径层级错误；不要在预填路径附近反复尝试。
3. 依赖结论多源交叉判定，缺一不可的五源检查：包管理器清单字段 + import 面扫描（逐条甄别标准库/内部互引/第三方）+ 清单外配套存在性（requirements.txt/lock/vendor 目录）+ vendored 文件头注释（来源与版本线索）+ 临时目录依赖甄别（一次性脚本不上浮进规范）。
4. 命中"声明"后必须核"安装"：require 字段存在不代表已安装，检查 vendor/ 目录或 lock 文件是否配套。
5. 粒度受限的文档只收录实测通过的事实；被证伪的预填事实在交付说明中显式纠正（给出修正后的实际路径/位置），防止下游引用者继承错误基线。

## Faster Next Time
- 预填路径核验失败的第一反应 = 按文件名全仓库 glob，一次定位即可修复路径层级漂移；连续两次独立定位失败（glob 空 + 读取报错）即认定预填路径失真，停止原路径试探。
- 依赖清点五问检查单：清单字段是什么？import 面有无第三方？有无 lock/vendor 配套？有无 vendored 内嵌源码？temp/ 类一次性依赖是否被误入清单？
- 静态扫描计数（如 0 条）永远只作线索；当它与任何已知事实矛盾时，以实测为准。

## Applicability Boundaries
- 适用于：以预填事实/材料基线为起点的文档、规范、知识库生成任务；依赖审计与清点；目录迁移后的基线同步检查。
- 不适用于：运行时故障定位（应走日志/trace 证据链，路径失真不是主因场景）；基线由用户即时现场提供且刚核验过的事实（矛盾概率低，但抽查仍值得）；基线核验通过后无需在同一任务内反复重验。
- 反模式：把核验三步写成抽象原则而无失败分支；用单一静态扫描计数直接下"零依赖"结论；把一次性脚本依赖上浮进正式规范。

## Evidence or Examples
- 派工单预填 `dvwa/includes/Parsedown.php`，glob 与 Get-Content 双双失败；按文件名 `**/Parsedown.php` 全仓 glob 命中实际路径 `DVWA/dvwa/includes/Parsedown.php`（顶层模块目录内还有一层同名子目录，双重前缀导致预填路径歧义）。
- workflow_base 预填为顶层独立目录，实测位于 `workspace/02_软件源码/` 下；其 CLI 入口头部仅标准库 import，与预填"纯标准库"结论一致（位置错、结论对，仍须按实测位置落笔）。
- composer.json require `zircote/swagger-php ^4.10`，但仓库无 vendor 目录——"有声明无安装"，清点时按声明态记录而非已安装态。
- Python 侧零第三方依赖由两源共同佐证：pyproject.toml:6 `dependencies=[]` + imports.json 58 条 import 逐条甄别为标准库/内部互引。
- vendored 库两处：Parsedown.php（文件头含作者与许可信息）、recaptchalib.php（内嵌 reCAPTCHA 实现），均不经包管理器，静态清点天然盲区。
- temp/ 目录的 faster-whisper 为一次性素材转写脚本依赖，判定为非正式依赖，未上浮进规范文档。