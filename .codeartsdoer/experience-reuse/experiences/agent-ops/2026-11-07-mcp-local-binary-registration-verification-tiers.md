---
id: 2026-11-07-mcp-local-binary-registration-verification-tiers
title: 本地二进制 MCP 服务注册的三层验证与跨会话重载边界
category: agent-ops
nature: technique
created_at: 2026-11-07T08:51:58
updated_at: 2026-11-07T08:51:58
tags: [mcp, agent-platform, verification-tiers, stdio, session-boundary]
keywords: [mcp_settings, stdio, cairn-mcp, 本地命令注册, 运行时可见性, 新会话重载, 配置校验, 回退路线]
problem_patterns: [MCP 注册后当轮会话看不到新服务, MCP 配置写入后如何验证成功]
source_sessions: [ses_e4c8a78edffee772ytCDqwOSfb]
project: Date
severity: medium
quality_score: 89
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: ["2026-11-06-shell-session-state-not-persistent", "2026-11-06-codeartsdoer-skill-market-registry", "2026-11-07-minimal-instance-format-probing"]
---

# 本地二进制 MCP 服务注册的三层验证与跨会话重载边界

## Scenario

把本地构建出的二进制可执行文件（如 Cairn 的 `cairn-mcp.exe`）注册为 IDE/Agent 平台的 MCP 服务（stdio 型），需要在**不中断当前会话**的前提下判断注册是否成功，并决定是否继续投入验证成本。

## Key Signals

- 配置文件写入成功、JSON 解析通过、command 路径实存——但当轮会话的工具清单里**看不到**新 MCP 服务。
- 第一反应容易判为"注册失败"，进而重复改配置或提前回退——这是误判点。

## Essence

注册验证分三层，**当轮会话只能完成第一层**：

1. **配置合法性**（当轮可验）：JSON 可解析、command 指向的文件实存、env 字段无凭据泄漏。
2. **运行时可见性**（须平台重载/新会话）：服务被平台加载并出现在工具清单——受会话边界约束，当轮"看不到"是**边界现象而非失败**。
3. **功能可达性**（调用时验）：服务真实响应；须提前准备非 MCP 的备用路线（如 CLI 直调）兜底。

把第二层误判为失败，代价是重复配置、误回退或放弃可用路线。

## Approach

1. 写前备份原 `mcp_settings.json`（零破坏纪律）。
2. 写入 stdio 注册项：`command` 用绝对路径，`env` 保持空对象（本地命令型通常无需凭据）。
3. 当轮只验第一层：`ConvertFrom-Json` 解析 + 路径存在性 + env 属性数为 0。
4. 显式登记"运行时可见性待新会话重载"，**不在当轮反复重试加载或回改配置**。
5. 保持备用路线（CLI 直调同一二进制）可用并实测一次，功能可达性不悬空。
6. 新会话首个动作验证第二层（工具清单可见性）；不可见再回查配置。

## Faster Next Time

- 校验脚本模板：解析 + 路径 + env 计数三查，一次并行完成。
- 见到"当轮看不到新服务"→ 先查会话边界，再查配置；禁止当轮反复重试。
- 注册任何新 MCP 服务前，先确认其 CLI 等价路线可用——MCP 是增强不是唯一通路。

## Applicability Boundaries

- 适用：stdio 本地命令型 MCP 注册；带会话隔离机制（新会话才重载配置）的 Agent 平台。
- 不适用：http/SSE 远程 MCP（连接模型不同，当轮即可验）；无会话重载边界的平台（当轮应可见，看不到才是失败）。
- 平台特定性：验证于 CodeArts Agent（码道）；分层验证思路为通用模式。

## Evidence or Examples

- 实例（2026-11-07）：写入 `{"mcpServers":{"cairn-mcp":{"command":"D:\\refs\\Cairn\\bin\\cairn-mcp.exe","args":[],"env":{}}}}`；当轮校验 `json-valid: True`、command 实存、`env-props: 0`；运行时可见性登记为待新会话验证；CLI 备用路线（`cairn` 主命令 7 个子命令）当轮实测 exit 0。
- 平台证据：同一会话早前已实证 `agents/*.md`、`skills/*/SKILL.md` 均为"落盘即注册"，但 MCP 配置不走此机制——不同注册面有不同的生效时机，须分别实证。