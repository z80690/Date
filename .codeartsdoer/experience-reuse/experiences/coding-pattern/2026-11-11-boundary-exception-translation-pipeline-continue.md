---
id: 2026-11-11-boundary-exception-translation-pipeline-continue
title: "降级继续"设计要求边界函数把第三方异常统一翻译为领域异常，否则异常类型穿透 catch 中断全链路
category: coding-pattern
nature: pitfall
created_at: 2026-11-11T00:24:41
updated_at: 2026-11-11T00:24:41
tags: [异常翻译, 领域异常, 降级继续, 边界函数, 容错设计]
keywords: [URLError 穿透, DNS 解析失败, 异常类型收口, except 领域异常, 降级路径失效, 流水线中断, 边界翻译, fail-continue, 官方渠道失败, 如实登记]
problem_patterns: [设计意图是"外部资源获取失败→如实记录→降级继续"，实测却整段流水线异常中断，因为第三方库抛出的异常类型（URLError/DNS 错误）不在 catch 的领域异常范围内, 边界函数只在预期路径上抛领域异常，未预期路径（网络层、编码层）的原始异常直接穿透到调用方, 单元测试全绿但真机一跑网络不通就崩，容错分支从未被真实异常类型触达]
source_sessions: [ses_e3a9c97a3ffeCp9OO263dGGrPC]
project: Date
severity: medium
quality_score: 87
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-10-os-replace-winerror5-transient-lock-retry, 2026-11-10-persistence-reveals-idempotency-gaps-registration]
---

# "降级继续"设计要求边界函数把第三方异常统一翻译为领域异常，否则异常类型穿透 catch 中断全链路

## Scenario

流水线步骤含外部资源获取（下载安装包、拉取仓库、调远程接口），设计规格明确"官方渠道获取失败→如实登记→对应任务拒跑但其余步骤继续"。实现者在边界函数里只对预期失败路径 raise 领域异常（如 PrepareError），调用侧 `except PrepareError` 落降级分支。单测全绿；真机一跑，官方域名 DNS 解析失败抛 `urllib.error.URLError`，不在 catch 范围，整个驱动脚本当场中断。

## Key Signals

- 失败栈最顶层是第三方库异常类型（`URLError: <urlopen error timed out>` / `NameResolutionError: getaddrinfo failed`），而非领域异常。
- 规格里写了降级继续，现象却是整段停摆——"规格承诺"与"异常类型覆盖面"对不上，这是判别信号：查 catch 子句捕获的异常类型集合 vs 边界函数可能抛出的异常类型集合。

## Essence

降级继续是一种**按异常类型分发的控制流**：catch 声明的类型集合就是降级路径的实际覆盖面。边界函数若把第三方原始异常放行，等于让 catch 的覆盖面由第三方库的实现细节决定——规格写再多的降级条款也不会生效。正确做法：边界函数用 `except Exception` 收口，把一切失败（含未预期类型）翻译为携带原因的领域异常，使调用方的降级分支成为唯一出口。这是异常边界翻译（exception translation）在容错流水线上的硬性含义，不是风格偏好。

## Approach

1. 盘点边界函数（凡包装网络/子进程/文件系统等外部调用的函数）可能穿透的异常类型，对照调用方 catch 的类型集合，列出缺口。
2. 在边界函数外部动作调用点套 `try: ... except Exception as e: raise DomainError(CODE, f"官方渠道获取失败：{e}") from e`——保留原因链，异常类型统一。
3. 领域异常消息必须含降级决策所需信息（失败环节、原始原因、规格依据条款号），让降级分支"如实登记"有内容可写。
4. 验证容错分支不能只靠单测：加一条真实故障注入测试（断网/无效域名），断言"该步骤拒跑 + 其余步骤继续跑完 + 全量汇总 still 产出"。

## Faster Next Time

- 写任何"失败→降级继续"规格时，同步给实现加检查项：边界函数是否 `except Exception` 收口？未收口视为规格未落实。
- 代码评审检查点：搜索 `except <领域异常>` 的调用方，向上追被调函数内所有 raise 点，凡有非领域异常 raise 的都记缺陷。
- 更早发现：容错分支的单测别只 mock 领域异常，用一个真实第三方异常类型（如抛 URLError 的 stub）做注入测试。

## Applicability Boundaries

- 适用于任何"部分失败不阻断全局"的流水线/批处理设计，语言不限（Python 的 except 类型分发、Java 的 catch 多态同理）。
- 不适用于：失败必须立即终止的 fail-fast 场景（此时收口反而吞掉终止信号）；以及顶层兜底边界（那里收口是合理的，本条讲的是中间层）。
- 注意 `except Exception` 收口仅限边界函数内部，不要扩散到业务逻辑层，否则掩盖真实 bug。

## Evidence or Examples

- 本会话环境准备流水线：`_source_check` 下载 Tor 官方安装包，`vod/dist` 域名 DNS 失败抛 `urllib.error.URLError`，驱动脚本在组 7 中断（首轮 all_pass=false 的间接成因之一）；修为 `except Exception → PrepareError(SOURCE_FAIL, 原因链)` 后，Tor 未就绪被如实登记，通讯隐匿/Tor 两场景按 5.2.1 规则 10 拒跑，其余场景继续，`run_final.py` 最终 all_pass=true。
- 修复要点实录：领域异常消息保留规格条款指针（"5.2.3 异常 4"）与原始原因，拒绝场景的回执里因此有完整可审计的失败链。