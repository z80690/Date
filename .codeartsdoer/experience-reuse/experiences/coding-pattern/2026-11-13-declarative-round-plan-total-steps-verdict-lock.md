---
id: 2026-11-13-declarative-round-plan-total-steps-verdict-lock
title: "状态机完成态禁从已见步骤推断：轮计划声明式声明 total_steps，防首步回执提前锁终态"
category: coding-pattern
nature: methodology
created_at: 2026-11-13T12:33:44
updated_at: 2026-11-13T12:33:44
tags: [状态机, 回执协议, 轮次计划, 终态锁, 设计模式]
keywords: [start_round total_steps 声明式计划, verdict_pending 提前进入, dispatch requires running state, E_FRAMEWORK_OFFLINE 误导性错误码, 已见步骤推断完成态, 多步骤轮锁死, 回执驱动迁移, 步骤计数判据]
problem_patterns: [状态机从"已收到回执的步骤"推断轮完成态，多步骤轮在首步回执后即转终态，后续步骤派发被拒且报出的错误码指向无关原因（框架离线）, 步骤派发前不声明轮内步骤总量，完成判定依据随执行进度漂移]
source_sessions: [ses_e2d1b45edffeiZTF0xjq1cyv7a]
project: Date
severity: medium
quality_score: 86
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-13-restricted-agent-adapter-literal-ip-jsonl-verdict, 2026-11-06-event-driven-mechanism-liveness-single-fact-source]
---

# 状态机完成态禁从已见步骤推断：轮计划声明式声明 total_steps，防首步回执更新后锁终态

## Scenario

回执驱动的演练轮次状态机：每轮含多个原子步骤（如 step-1 伪装、step-2 心跳），每步 dispatch → 执行 → receipt 回执。轮状态流转 running → verdict_pending（判定挂起，锁死新派发）。实现按"所有已登记步骤均 DONE 即转 verdict_pending"判定——但"已登记步骤"是随派发动态增长的集合，轮内实际步骤总量从未被显式告知状态机。结果：step-1 回执成功后，状态机认为"全部已知步骤完成"，轮转入 verdict_pending，step-2 派发被拒。

## Key Signals

- **误导性错误表象**：step-2 派发报 `E_FRAMEWORK_OFFLINE: round 6 is verdict_pending; dispatch requires running state`——错误码字面指向"框架离线"，真实原因是轮状态提前进入终态。错误码与根因错位，容易把排查引向框架健康检查。
- **时序指纹**：第一轮回执（ack1）返回的 state_next 不是 running 而是 verdict_pending/终态——单步回执后立即终态化，本身就是"完成判据过松"的信号。
- **判别问题**：问一句"状态机怎么知道这轮共有几步？"——若答案是"看已派发了几步"，即存在本缺陷。

## Essence

状态机的**完成态判定依据必须是显式声明的计划总量，而非已观察到的步骤集合**。"已见步骤全部 DONE"在增量派发模型下恒真于每一步之后——把执行进度当成了完成判据。正确模型：轮开启时声明式登记 `total_steps=N`（计划先行），每轮回执后判定 `done_steps >= total_steps` 才转 verdict_pending；任一步 failure 则转 round_failed。声明式计划同时带来校验红利：实际派发步数超出计划可即时报警（计划与执行漂移检测）。

## Approach

1. **轮开启即声明计划**：
   ```python
   def start_round(self, round_no: int, total_steps: int) -> RoundState:
       self._plans[round_no] = total_steps      # 计划先行，禁省略
       self._rounds[round_no] = RoundState.RUNNING
   ```
2. **回执后按计划判完成**：
   ```python
   def _round_state_after(self, round_no: int) -> RoundState:
       steps = [s for s in self._steps.values() if s.round_no == round_no]
       if any(s.state == StepState.FAILED for s in steps):
           return RoundState.ROUND_FAILED
       if len(steps) >= self._plans[round_no] and all(
           s.state == StepState.DONE for s in steps
       ):
           return RoundState.VERDICT_PENDING    # 计划步数满足才终态化
       return RoundState.RUNNING
   ```
3. **派发时校验计划内**：step_no 超出 total_steps 的派发直接拒绝（计划漂移检测），而非静默接受。
4. **错误码语义对齐**：状态未就绪类拒绝用独立错误码（如 E_ROUND_NOT_RUNNING），不复用框架离线码——错误码必须能区分"哪一层拒绝"。

## Faster Next Time

- 设计评审检查点：任何"从已见元素推断完成"的状态机（批量任务、流水线、多阶段审批）都改为声明式总量先行；提问模板："完成判据里有没有会随执行增长的集合？"
- 更早发现：单测加两条——①双步轮：step-1 回执后断言 state==running（此用例在缺陷版必挂）；②step_no 超计划的派发必须被拒。
- 错误码复盘信号：出现"错误码字面意思与真实根因不符"时，先怀疑状态机提前终态化这类语义错位，再查错误码字面所指层。

## Applicability Boundaries

- 适用：回执/事件驱动的多步骤轮次编排（演练轮、审批流、批处理阶段机）；任何"完成态判定依赖动态增长集合"的状态机。
- 不适用：单步骤轮（无提前锁死问题，声明 total_steps=1 亦可统一口径）；步骤数天然不可预知的流式处理（此时完成判据应为显式结束信号而非计数）。
- 边界：total_steps 声明后若用户中途追加步骤，需走计划修订通道（更新声明值并留痕），禁静默放宽；步骤失败转 round_failed 的优先级高于完成判定（失败即锁，不因计数达标而放行）。

## Evidence or Examples

- 实证会话（P003 round-06/07）：round-06 两步轮在 step-1 回执后转 verdict_pending，step-2 dispatch 报 `E_FRAMEWORK_OFFLINE: round 6 is verdict_pending; dispatch requires running state`（receipt.py `_round_state_after` 从已见步骤推断）；修复为 `start_round(round_no, total_steps=2)` 声明式计划后，round-07 实测 ack1=running → ack2=verdict_pending，两步轮完整走通。
- 修复位置：adapter/receipt.py（start_round 增 total_steps 参数、_round_state_after 改计划计数判据）；Ruff 全过+pytest 回归通过。
- 关联事实：该缺陷在无抓包的单步轮（round-04/05）中不显现——多步轮+回执驱动两者同时存在才会触发，单测若只覆盖单步轮则漏检。