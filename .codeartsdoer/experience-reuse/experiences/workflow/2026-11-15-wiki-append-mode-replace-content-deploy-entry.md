---
id: 2026-11-15-wiki-append-mode-replace-content-deploy-entry
title: Wiki 配置命令小节的追加型 replace_content：增量部署入口保留原条目逐字不变、末尾追加条目与文件级 code_refs 首建
category: workflow
nature: decision
created_at: 2026-11-15T20:39:23
updated_at: 2026-11-16T00:01:54
tags: [wiki修订, 追加型patch, 增量新增, 部署入口, 文档小节]
keywords: [replace_content, 追加型, 重述型, 逐字保留, 末尾追加, 部署入口, api/index.py, Vercel serverless, code_refs 首建, 文件级引用, 实现细节不进正文, 解耦声明]
problem_patterns:
  - 新增部署入口/配套部署配置等增量文件落入既有模块文档的配置命令类小节时，误用"按口径重述全部条目"的重述型 replace_content，凭记忆重写本已正确的既有条目引入失真
  - 追加部署条目时罗列入口文件内部实现（WSGI 类名、响应头构造、内部常量），污染配置命令层面的条目式行文粒度
  - 受影响小节在索引中此前无 code_refs 记录，不知首建引用该用文件级还是行级锚点，硬凑行级依据
source_sessions: [ses_e243a21d9ffeJYc5m6okuLhehx]
project: Date
severity: low
quality_score: 84
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: A
related_experiences: [2026-11-08-wiki-section-same-layer-action-criteria, 2026-11-14-wiki-unchanged-baseline-increment-body-refs-routing, 2026-11-12-wiki-added-diagnostic-probes-body-exclusion, 2026-11-08-wiki-section-revision-patch-json-mode]
---

# Wiki 配置命令小节的追加型 replace_content：增量部署入口保留原条目逐字不变、末尾追加条目与文件级 code_refs 首建

## Scenario

以只读修订 subagent 身份接收 Wiki 小节级修订派工（patch JSON 输出契约、禁止直改文档）。本轮变更集仅 1 个 added 文件——项目的 Vercel serverless 部署入口 `api/index.py`（自包含 WSGI 应用、零第三方依赖、任意路径返回 200 OK JSON 状态），归属既有 adapter 模块承载。受影响小节是 `codebase-knowledge/P003演练适配器.md` 的"配置与命令"小节（条目式，既有 4 条：构建安装/白名单/证据目录/框架就绪单点），派工单预判"部署入口与部署环境配置同层面 → replace_content"，并明示该小节在索引中此前无 code_refs 记录、本次为首次建立。修订者独立执行、单轮闭环。

## Key Signals

- 变更性质信号：变更集是"新增文件"（增量扩容）而非"口径改版"（条数/条目/维度变化）——既有 4 条条目与新增部署入口互不冲突，没有任何需要删除或改写的内容。
- 同层面信号：小节关注"构建/安装/运行命令与部署环境配置"，部署入口文件与该层面同层面（判据与 2026-11-08-wiki-section-same-layer-action-criteria 同源）。
- 兜底信号：派工单明示禁止罗列实现细节（不写 RequestHandler 类/响应头构造等内部实现）、不写内部常量/函数/类型清单——配置命令小节只承载"命令与配置入口"，不承载代码结构。
- code_refs 信号：小节此前无引用记录（首建），且部署入口是单文件整体语义、无特定行号锚点意义。

## Essence

同层面判定成立后，`replace_content` 还有子模式选型，按变更性质二分：**口径改版 → 重述型**（按新口径重述全部条目、删除已废维度、不留残句）；**增量新增 → 追加型**（既有条目逐字保留 + 末尾追加新条目，绝不动原文）。增量新增场景下误用重述型等于凭记忆重写本已正确的内容——纯失真风险、零收益。追加条目按固定要素模板行文：入口文件定位 + 关键属性（自包含/零依赖等）+ 与核心包的解耦及角色声明（如"仅供部署探活"）+ 配套配置关系（部署配置文件的转发规则），1-2 句 60-90 字；实现细节（类名、响应头构造、内部常量）一律不进正文。code_refs 首建时，部署入口类单文件语义用文件级 `:1`。

## Approach

1. **同层面判定**：问"新增文件与小节已有关注点是否同层面"——部署入口 vs 配置命令小节 → 同层面，进入 replace_content。
2. **变更性质二分选子模式**：变更集只有 added 且与既有条目无口径冲突 → 追加型；条数/条目/维度变更（改版）→ 重述型；仅波及不承载 → line_number_only。
3. **追加型执行**：既有条目从派工单提供的当前内容**逐字复制、一字不改**；末尾追加 1 条按要素模板行文（入口定位 + 关键属性 + 解耦/角色声明 + 配套配置关系），控制在 60-90 字。
4. **实读核验后动笔**：实读新增文件全文确认与派工单源码片段一致；grep 定位小节实文确认与派工单声称的"当前内容"一致——派工单材料是对照，实文才是写入依据。
5. **code_refs 首建**：小节无既有记录时，新增引用数组即为首建集合；部署入口用文件级 `文件路径:1`，不为单文件语义硬凑行级锚点。
6. **输出严格 JSON 直出**：`{"wiki_file", "patches": [{"section_title", "action", "new_content", "code_refs"}]}`，无 markdown 包裹。

## Faster Next Time

- 选型口诀：变更集只有 added（无口径冲突）→ 追加型；条数/条目/维度变了 → 重述型；只波及但格式/关系未变 → line_number_only。
- 警惕信号：派工单出现"保留原 N 条逐字不变 + 末尾追加"即追加型的显式声明；出现"按新条数重述/删除已废维度"即重述型；两类措辞混入同一派工单时逐节二分。
- ROI：追加型把修订成本压到"1 条新条目 + 0 处既有条目校对"——逐字保留使既有内容零失真风险，省去重述型的逐条比对。
- 反模式：对增量新增凭记忆重写全部条目（重述型误用）；把 WSGI 类名/响应头构造/内部常量写进配置命令小节；为部署入口硬凑行级锚点；只交新增条目却丢掉既有条目（replace_content 的 new_content 必须是替换后的完整正文）。

## Applicability Boundaries

- 适用：patch JSON 小节级修订流程中，增量新增文件（部署入口、脚本、工具类文件）落入既有模块文档的配置/命令/清单类条目式小节；小节 code_refs 首建场景。
- 不适用：口径改版后的条目重述（走重述型，见 2026-11-08-wiki-section-revision-patch-json-mode）；批次数值型资产扩容（有统计计数联动问题，见 2026-11-14-wiki-unchanged-baseline-increment-body-refs-routing）；不同层面的状态类变更（仅 line_number_only）；诊断探针/实现细节类文件（正文整体排除，见 2026-11-12-wiki-added-diagnostic-probes-body-exclusion）。
- 前提约束：修订者不直改文档、以 patch JSON 交付；派工单自带受影响小节当前内容与变更文件源码，修订者实读核实而非重扫全库。
- 证据等级：单次顺利闭环（一次通过、无失败对照），追加型/重述型二分的跨场景稳定性待同类任务复用检验。

## Evidence or Examples

- 源会话 ses_e243a21d9ffeJYc5m6okuLhehx（@general 修订 subagent，trace 内联提供，Date 项目 adapter 模块）。
- 变更集：`api/index.py`（added，33 行，Vercel serverless WSGI 入口；`SERVICE_NAME = "p003-drill-adapter"`；`RequestHandler.__call__` 任意路径返回 200 OK JSON；配套 `vercel.json` builds 用 @vercel/python、rewrites 全路由转发）。
- 追加条目实证：`- 部署入口：Vercel serverless 入口 api/index.py（自包含 WSGI 应用，零第三方依赖，与 adapter 包解耦，仅供部署探活）；vercel.json 将全部路由 rewrite 转发至该入口。`（原 4 条逐字保留在其前）。
- code_refs 首建实证：`["api/index.py:1"]`——该小节索引中此前无引用记录。
- 兜底执行实证：RequestHandler 类、`__call__` 签名、响应头构造（Content-Type/Content-Length）、`SERVICE_NAME` 常量均未进入 patch 正文，仅以"自包含 WSGI 应用、零第三方依赖"属性词概括。