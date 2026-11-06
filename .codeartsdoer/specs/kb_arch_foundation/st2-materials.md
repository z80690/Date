# ST2 学习材料清单（kb_arch_foundation）——终版

> tasks 9.1 落盘载体。**材料齐（5 论文+5 项目，全部经 webfetch/GitHub API 实证）**。P4 超窗入选【用户裁决 2026-11-07】。建立：2026-11-07。最后核验：2026-11-07。

## 论文（5/5 齐）

| # | 名称 | 角度 | 出处 | 时间 | 状态 |
|---|------|------|------|------|------|
| P1 | The Landscape of Agentic Reinforcement Learning for LLMs: A Survey | Agent 架构与能力分类+开源框架全景 | arXiv:2509.02547（TMLR） | 2025-09（v5 2026-04） | 已验证入选 |
| P2 | Advances and Challenges in Foundation Agents | 模块化架构/自进化/多代理/安全 | arXiv:2504.01990 | 2025-03（v2 2025-08） | 已验证入选 |
| P3 | Multi-Agent Collaboration Mechanisms: A Survey of LLMs | 多代理协作机制（Router/Worker 编排理论） | arXiv:2501.06322 | 2025-01 | 已验证入选 |
| P4 | Agent Workflow Memory（AWM） | 工作流记忆=经验沉淀机制 | arXiv:2409.07429（CMU） | 2024-09 | **入选【用户裁决：超窗 2 个月经典性取舍】** |
| P5 | A Lean and Spec-Driven AI-Assisted Software Development Lifecycle: The AI-SDLC Approach | SDD 方法论（spec+AGENTS.md+阶段化技能文件+受约束自主） | arXiv:2609.24348（URAI 2026 发表） | 2026-09 | 已验证入选（arXiv 搜索页实证） |

## 项目（5/5 齐）

| # | 名称 | 出处实测 | 质量评估 | 相关性 | 正反例属性 | 状态 |
|---|------|---------|---------|--------|-----------|------|
| J1 | microsoft/autogen | 61,734⭐/9,378 fork，2026-10-28 推送，CC-BY-4.0 | 大厂+高引用+框架+活跃 | 多代理对话编排 | **正例**（工业级多代理实现） | 已验证 |
| J2 | langchain-ai/langgraph | 44,580⭐/7,679 fork，2026-11-06 推送，MIT | 高引用+框架+活跃 | 图式编排（状态机式 agent 流） | **正例**（图编排=本单状态机参照） | 已验证 |
| J3 | langgenius/dify | **160,567⭐**/25,406 fork，2026-11-06 推送 | 极高引用+agentic 框架+活跃 | 低代码 agentic workflow+MCP+skills | **正例**（可视化编排）+**反例素材**（自定义 License 争议=开源治理反例） | 已验证 |
| J4 | FoundationAgents/MetaGPT | 71,200⭐/9,092 fork，MIT，**pushed_at=2026-01-21（10 个月未推送）** | 高引用+多代理框架 | SOP 化多代理软件公司 | **反例**（维护活跃度衰减：高星但近 10 个月无推送——引用度≠维护度） | 已验证（活跃度标注） |
| J5 | OpenHands/OpenHands | **92,828⭐**/12,387 fork，2026-11-06 推送，MIT | 极高引用+AI 开发框架+活跃 | 自主开发 agent 运行时 | **正例**（agent 运行时工程化） | 已验证 |

## 补充反例素材（≥1 纪律满足）

1. MetaGPT 活跃度衰减（高星低维护）——反例：引用度不等于可依赖性。
2. deepseek-super-agent（12⭐个人维护，U8）——反例：作为学习材料不满足大厂高引用门槛。
3. Cairn check-invariants Windows sh 兼容缺陷（本单实战）——反例：跨平台构建脚本的 shell 兼容性坑。
4. 2501.12594/2411.17202/2308.11432 三个错误 ID 淘汰——反例：凭记忆引用论文 ID 的编造风险（验证机制拦截）。

## 淘汰记录（验证机制拦截编造风险）

- 2501.12594 → 人形机器人论文（主题无关）
- 2411.17202 → 粒子探测器论文（主题无关）
- 2308.11432 → 经典 agent 综述但 2023-08 首发，超窗 3 年（不满足近 1 年门槛）

## 与考核目标关联

P1/P2→四层分层与能力模块；P3→Router/Worker 编排；P4→经验沉淀与工作流复用；P5→SDD 生命周期；J1/J2/J3/J5→编排与运行时工程正例；J4+补充素材→反例教训。