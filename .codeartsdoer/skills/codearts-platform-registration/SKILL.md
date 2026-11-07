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
- listSkills 枚举边界（2026-11-08 实测）：listSkills 返回清单仅枚举 SKILL.md 技能条目（实测 58 项全为技能），**不单列 agents/*.md 持久化子智能体**；全 deny 的智能体在所有技能的 agents 挂载字段均无痕迹——因此"listSkills 查不到子智能体"≠"未注册"。注册生效的权威验证=Task 派工实际运行（子代理按配置 SOP 执行并返回产物，行为指纹逐条对齐新版配置即证明现行配置已生效）；listSkills 枚举边界现象按会话边界登记，新会话重载后可复验
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
- 华为云文档站 support.huaweicloud.com 的 EdgeOne 拦截=**UA 检测**（无 UA 返回 Security Verification 页；带标准浏览器 UA 即 200 直抓 .md/llms.txt——已实证修复）。**browser 内置浏览器不是抓取通道**（仅返回"打开成功"回执给用户，Agent 读不到页面内容——已证伪"browser 为解锁候选"）；SPA 搜索页（developer/bbs.huaweicloud.com）可达无验证码但结果 JS 渲染，静态抓取 0 条数据
- 规则（.mdc）与 metadata.properties 只能用户经设置界面创建/修改，Agent 只产出草稿供粘贴

## Knowledge/RagSearch 平台检索边界（第 0 层实验实证）
- Knowledge 检索对象=`.codeartsdoer/.codebase/` 平台自动生成的知识快照（codebase-knowledge/project-knowledge）：**时效滞后**（updated_at 停留在快照生成日，当日更新的文档不在快照）且不覆盖 notes/ 手写知识库——命中的旧快照不可当现行状态，须与索引现行条目交叉核验
- RagSearch=企业知识库通道，未接入企业知识库时恒返回"No relevant content found"（本项目 N/A）
- 第 0 层实验判定模式（可复用）：3 主题双路对比（A=索引→命中条目→读文件；B=平台检索直查）+**锚点命中计数**（命中验收锚点才算，相关旧快照不算）；命中锚点≤2/3→判定"降为补充"（平台检索仅作按需手动全文检索补充，写路径与读路径主链仍唯一走索引）；Knowledge 的 build_index 模式可重建快照（登记为后续可选项）
