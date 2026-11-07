---
name: codearts-platform-registration
description: CodeArts Agent（码道）平台的技能/子智能体/MCP 注册机制与验证方法：文件落盘即注册、listSkills 运行时权威源、agents/*.md frontmatter 格式、mcp_settings.json 格式、经验库注入通道。凡涉及创建技能/智能体、验证注册、接入 MCP、经验库机制时使用。
---

# 码道平台注册机制（实证版）

## 技能注册（已实证）
- 载体：`.codeartsdoer/skills/<id>/SKILL.md`，YAML frontmatter 必含 `name`（=目录名，动宾结构）+ `description`（触发条件+适用+不适用三要素）
- **文件落盘即注册**：ProjectSkillStatus.txt 自动追加 `<id>=true`，listSkills 同步可见，无需重启
- 脚本捆绑：`skills/<id>/scripts/*.ps1` 随技能交付，frontmatter 正文写调用说明

## 持久化子智能体注册（test_mini/examiner/grader 实证）
- 载体：`.codeartsdoer/agents/<id>.md` = YAML frontmatter + Markdown 正文提示词
- frontmatter 字段：`description`（触发条件+能力+不适用）、`mode: all`（子智能体形态语义由 description 承载）、`tools`（最小白名单，未列即禁用）、`permission.skill`（`'*': deny` 默认拒绝 + `<skill>: allow` 白名单，禁 '*' 授权）、`disable`（false 启用/true 禁用即退出挂载）、`scope: project`、`avatar`
- **文件落盘即注册**：listSkills 的 skills[].agents 字段出现该智能体名（仅 permission.skill allow 的技能显示挂载；全 deny 的智能体无挂载记录=正常）
- 验证方法：listSkills 观察挂载形态；派工调用方式首次使用时实测并回写登记
- 运行时派工双通道：Task 工具临时 Worker（隔离会话，会话存档于 `C:\Users\Administrator\.codeartsdoer\agent-team\session\ses_*`）+ agents/*.md 持久化注册

## MCP 注册
- 载体：`.codeartsdoer/mcp/mcp_settings.json`：`{"mcpServers":{"<id>":{"command":"<exe 路径>","args":[],"env":{}}}}`
- 写入后 JSON 校验（ConvertFrom-Json）+零凭据核验；**新会话重载后工具才可见**（当前会话不可实测，登记待验证）
- 失败回退：保留原文件备份，CLI 直调等备用路线不拆除

## listSkills = 运行时权威源
- 技能总数/挂载关系/启用状态以 listSkills 返回为准；ProjectSkillStatus.txt 作交叉核对；磁盘文件为事实源
- disable=true 的智能体自动退出所有技能挂载清单

## 经验与记忆注入通道（平台原生，非脚本）
- 会话启动：MEMORY.md 索引+相关记忆自动注入
- 消息事件：experience_retrieve 按关键词检索经验注入
- 规则：session-rules 块每轮注入，内容 diff 即规则变更信号，变化须立即采用
- 反思窗口（00:00–06:00）为唯一既有定时性兜底；**禁自建任何定时任务**

## 平台能力边界
- 无文件 watcher/webhook（"文件变更"类事件用动作内嵌检查点实现）
- 华为云文档站 support.huaweicloud.com 可能被 EdgeOne 人机验证拦截（curl/webfetch 抓到 Security Verification 页=被拦，报原文+降级，browser 内置浏览器为解锁候选）
- 规则（.mdc）与 metadata.properties 只能用户经设置界面创建/修改，Agent 只产出草稿供粘贴
