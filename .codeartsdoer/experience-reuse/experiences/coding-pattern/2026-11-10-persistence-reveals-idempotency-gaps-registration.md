---
id: 2026-11-10-persistence-reveals-idempotency-gaps-registration
title: 新增持久化后必须重审注册入口幂等性——测试全绿不代表幂等安全
category: coding-pattern
nature: pitfall
created_at: 2026-11-10T23:34:39
updated_at: 2026-11-10T23:34:39
tags: [幂等, 持久化, 注册中心, 测试盲区, DUPLICATE_ID]
keywords: [幂等入口, 持久化, 重复注册, DUPLICATE_ID, 已存在不得覆盖, 测试盲区, 重启重挂载, 注册中心, 初始化, 单元测试局限]
problem_patterns: ["为注册中心/对象注册模块补持久化后，原先全绿的测试与验证脚本重跑即报'标识已存在且不得覆盖'", "幂等缺陷在无持久化时不可见：每次测试新实例内存态从零开始，重复注册路径单轮测试天然覆盖不到", "初始化函数（mount_defaults/register_defaults 类）被隐式约定为'进程内只调一次'，持久化合入后该隐约前提静默失效"]
source_sessions: [ses_e39f1f156ffeoDWfZpYxOFCkpt]
project: Date
severity: medium
quality_score: 88
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["coding-pattern/2026-11-10-arch-redline-as-core-purity-scan", "agent-ops/2026-11-07-write-receipt-not-proof-of-persistence"]
---

# 新增持久化后必须重审注册入口幂等性——测试全绿不代表幂等安全

## Scenario

注册中心/对象注册类模块（含"重复标识拒绝且不覆盖"约束）先实现并跑绿全部单元测试；随后为同一模块新增本地持久化（状态落盘、重启可恢复）。验证脚本第二次执行时，原本通过的初始化/挂载/注册步骤集体报"标识已存在"错误。

## Key Signals

- 报错形态：`CatalogError: 类目标识已存在且不得覆盖: <id>`、`ObjectError: 对象标识已存在: <id>`——都来自**保护性校验**（防覆盖），不是空指针或数据损坏。
- 触发时机精确对应"持久化合入"这一变更点：合入前重跑验证一切正常，合入后第二次跑即失败。
- 失败的都是"初始化/默认挂载/演示注册"类入口，而非用户主动的重复操作路径。

## Essence

幂等性缺口一直存在，只是被两个隐含前提掩盖：①单元测试每次新建实例，内存态从零开始，"同一存储上第二次注册"在单轮测试里**天然不可达**；②验证脚本此前只跑一次，从未触发重复路径。持久化把"第一次跑的写入"保留到了"第二次跑"，等价于给所有写入口补上了"重复调用"这个测试维度——暴露的**不是新 bug，而是既有的幂等假设失效**。持久化合入是写入口语义的放大器：所有"进程内只调一次"的隐含约定在持久化面前都必须显式化为幂等三分支。

## Approach

1. 变更检查点：任何模块引入持久化后，枚举其全部写入口（注册/挂载/初始化/默认装配），逐个回答"同一存储上被调用第二次会怎样"。
2. 注册入口统一改为幂等三分支，而非一律抛错：

```python
def register(self, obj):
    existing = self._store.get(obj.id)
    if existing is None:
        self._persist_and_add(obj)
        return "registered"
    if existing.equivalent_to(obj):   # 内容一致才放行
        return "already"              # 幂等成功，静默跳过
    raise DuplicateError(obj.id)      # 已存在且冲突，拒绝且不覆盖
```

3. 语义区分要保留：`already`（一致，幂等通过）与冲突拒绝是**两种不同结果**，不要合并成一个静默 return，否则真冲突会被吞掉。
4. 持久化合入后必须补一条回归用例："同一初始化序列在同一存储上执行两遍"——两遍都应成功且终态等价。
5. 防覆盖校验（拒绝覆盖）与幂等跳过并存不矛盾：前者保护"内容不一致的重复"，后者消化"内容一致的重复"。

## Faster Next Time

- 评审清单：凡见 `DUPLICATE_*` 类保护性抛错入口，追问一句"上层是否存在合法的重复调用路径（默认装配、演示流、验证脚本重跑、重启后重挂载）"。
- 信号前置：验证/演示类脚本会重复执行的，其调用的初始化入口**设计时就要按幂等写**，不要等持久化来暴露。
- 最低成本检测：合入持久化的同一轮，跑两次验证脚本（第二次即幂等回归），成本秒级。

## Applicability Boundaries

- 适用：任何带唯一键约束的注册/登记/装配类写入口（注册中心、适配器挂载、默认配置装配、缓存预热），尤其在引入持久化、重启恢复、脚本重跑语义时。
- 不适用：调用方明确要求"重复即失败"的强约束接口（此时保持拒绝语义，由调用方自行判重）；无唯一键的纯追加写入（如事件流水，本身可重复追加）。
- 边界提醒：幂等判定依据是"业务等价"，对象含时间戳/随机 id 字段时需要显式定义等价比较范围，否则幂等分支永远走不到。

## Evidence or Examples

- 实测：`verify_base.py` 第二次执行报 `CatalogError: 类目标识已存在且不得覆盖: embedded`（重复挂载被拒）与 `ObjectError: 对象标识已存在: xiaozhi_sim_01`（演示注册重复）。
- 修复：默认类目挂载与演示对象注册两个入口补幂等分支后，同一脚本连续执行全部通过（all_pass=true，50 单测全绿）。
- 修复前后测试结果不变（50/50）——证明单测无法捕捉该缺陷，回归必须靠"重跑验证脚本"这一真实重复路径。
- 来源：本会话编码轮次，证据等级=实测报错+修复后复跑验证。