---
id: 2026-11-13-restricted-agent-adapter-literal-ip-jsonl-verdict
title: "受限执行代理适配层四要素：白名单仅收 IP 字面量、校验链先验后连、JSONL 双流证据回查、判定函数不造数"
category: coding-pattern
nature: methodology
created_at: 2026-11-13T10:08:40
updated_at: 2026-11-13T10:08:40
tags: [安全适配层, 白名单校验, 越界即停, 证据流, 判定函数]
keywords: [ipaddress.ip_address 字面量校验, 主机名触发 DNS 外发泄漏, E_TARGET_DENIED 错误码分级, 校验链短路顺序, 越界全局开关, dispatches receipts JSONL 双流, 配对回查, 三态 success failure insufficient, 纯判定只读证据, 纯 stdlib 零依赖]
problem_patterns: [白名单校验直接接受主机名字符串，校验"通过"后连接时 DNS 查询本身构成外发且解析结果不受白名单控制, 校验与执行分离导致先连接后被拒，已建连接需要升级处置, 判定函数在抓包/日志证据缺失时默认返回 success，用造数掩盖证据链断裂]
source_sessions: [ses_e2f4e2eebffe77jZBS1o85Z7rc]
project: Date
severity: medium
quality_score: 89
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-11-boundary-exception-translation-pipeline-continue, 2026-11-12-local-dummy-llm-endpoint-egress-governance, 2026-11-10-dual-use-research-safety-redline-paired-clauses]
---

# 受限执行代理适配层四要素：白名单仅收 IP 字面量、校验链先验后连、JSONL 双流证据回查、判定函数不造数

## Scenario

需求契约要求实现"仅回环/白名单内可达、白名单外一律拒绝、越界即停、全程留痕、判定结果可核查"的受限执行适配层（EARS 接口契约逐条映射为代码）。实现时最易踩中的三处：白名单校验函数把主机名字符串也当合法目标放行；校验逻辑放在执行动作之后或与其并发，导致"先连后拒"；隐藏判定函数在 pcap/日志证据文件缺失时返回默认 success。四要素构成一套可复用的设计口径。

## Key Signals

- **主机名目标是隐形外发通道**：`socket.connect(("example.local", 80))` 之前发生 DNS 查询——查询本身是一次网络外发（可被劫持、可泄漏"要连谁"的意图），且解析出的 IP 完全不在白名单控制范围内。白名单校验若接受主机名字符串，"校验通过"是假的。
- **校验与执行时序倒置**：若任务先下发执行、后异步校验，被拒时连接已建立，处置从"拒绝（零外发）"升级为"阻断已建连接（E_BLOCK_FAILED）"——错误码分级被迫变复杂。
- **判定函数的默认值方向**：证据文件缺失/抓包中断/审计流为空时，若函数返回 `success` 或 `0 命中`，就是在无证据的情况下"造数"——安全判定必须三态：`success`（全量证据+全零命中+伪装有效）/ `failure`（任一命中，逐项列明）/ `insufficient`（证据链断裂，不判定）。

## Essence

受限代理的每一层都遵循"拒绝优先"：**入口层**白名单仅接受 `ipaddress.ip_address()` 能解析成功的 IP 字面量（含 CIDR 段匹配），主机名一律拒绝并留痕——把 DNS 从攻击面移除；**顺序层**校验链短路且先验后连（轮次状态 → 越界全局开关 → 白名单 → 框架就绪），任何一环失败即抛错误码、零外发动作；**证据层**下发与回执分流写 JSONL（dispatches/receipts 两流），验收时按 step_no 配对回查，证据与动作一一对应；**判定层**判定函数是只读纯函数，输入只有证据流与抓包产物，无证据 = `insufficient` 而非通过。四层共同保证：代码层面不可能发生白名单外外连，且每一个"通过"都能回放证据。

## Approach

1. **白名单仅收字面量**：
   ```python
   # 错误：接受主机名，校验后连接时触发 DNS 外发
   if target in allowed or resolve(target) in allowed: ...

   # 正确：字面量进、字面量出，主机名直接拒绝
   ip = ipaddress.ip_address(target)        # 主机名在此抛 ValueError
   if not any(ip in net for net in allowed_networks):
       raise AdapterError(E_TARGET_DENIED, target)   # 拒绝 + 拦截留痕，零外发
   ```
2. **校验链先验后连**：下发接口内按固定顺序完成全部校验（状态机轮次 running → 越界即停全局开关 → 白名单 → 框架就绪自检），最后一环通过才翻译下发框架；任何环失败短路返回对应错误码，不存在"部分执行"。
3. **错误码分级**：未连接被拒 = `E_TARGET_DENIED`（拒绝+拦截日志）；已建连接需阻断 = `E_BLOCK_FAILED`（升级处置+告警留痕）；证据缺失 = `E_EVIDENCE_MISSING`。分级让调用方（门禁/报告）能区分"防线起作用"与"防线被突破后补救"。
4. **JSONL 双流证据**：`dispatches.jsonl`（每条含 round_no/step_no/target/action/trigger）与 `receipts.jsonl`（handle_id/step_no/结论）分文件追加写；攻防配对检查 = 按 step_no 双向匹配，缺回执或缺下发分别对应不同错误码。
5. **判定函数不造数**：签名只吃证据（pcap 路径、审计流、计数），内部对每个判定项（明文命中=0/公网 IP=0/异常外连=0/伪装有效/日志干净）独立计数，聚合为三态；抓包不可用直接抛 `E_EVIDENCE_MISSING`，绝不返回默认值。
6. **依赖纪律**：纯 stdlib 实现（ipaddress/json/subprocess/pathlib），端口与进程核验走平台官方命令子进程（netstat/tasklist/docker ps），零第三方依赖——安全代码的审计面最小化。

## Faster Next Time

- 评审检查点三问：①白名单函数是否接受无法被 `ip_address()` 解析的字符串？②是否存在"校验通过后仍可修改 target"的路径（可变对象传引用）？③判定函数是否有证据缺失时的默认通过分支？任一"是"即缺陷。
- 更早发现：单测专门加两条——主机名目标必须被拒且无任何网络调用（mock socket 断言零调用）；删除证据文件后判定必须返回 `insufficient` 而非 `success`。
- 错误码先行：契约阶段就把拒绝/阻断/证据缺失三态错误码定进接口签名，实现时自然分层。
- 留痕路径用 JSONL 追加写而非内存列表收尾落盘——进程崩溃也不丢证据流。

## Applicability Boundaries

- 适用：本地授权演练/沙箱/受限执行代理等"目标集合白名单化 + 动作全程留痕 + 判定可核查"场景的适配层实现；语言不限，Python 示例以 3.11 实测。
- 不适用：一般业务服务的访问控制（白名单语义是身份而非外发面，DNS 处理逻辑不同）；不替代网络层防火墙/防火墙规则（本模式是应用层前置校验，纵深防御的一环）；目标必须用域名可达的真实业务（此时需把 DNS 解析器收敛为受控解析而非拒绝主机名，属另一模式）。
- 边界：IP 字面量策略对 IPv6 与 IPv4-mapped 地址需显式决定归一化口径；CIDR 匹配用 `ipaddress.ip_network` 的 strict=False。

## Evidence or Examples

- 本例实现（ses_e2f4e2eebffe77jZBS1o85Z7rc，P003 演练适配层）：15 文件纯 stdlib，IF-1/2 回执状态机 + IF-3/4 白名单与越界即停 + IF-5/6 端口与代理核验（netstat/tasklist/docker ps 三核验，0.0.0.0/公网绑定阻断留痕）+ IF-7/8/9/10 门禁/抓包会话/隐藏判定/攻防配对；判定五项 J1~J5（明文=0、公网 IP=0、异常外连=0、伪装 TLS 有效、日志干净）聚合三态。
- 门禁证据：`ruff check` 26 处违规迭代归零全过；`pytest tests/test_adapter.py` 20/20 PASSED（含主机名拒绝+证据缺失 insufficient 用例）。
- 白名单实测口径：W3=192.168.16.0/20（实测登记值），W4/W5 空集时禁自动发现——空集是合法状态，代表"无可达目标"，不是错误。