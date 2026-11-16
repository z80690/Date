# P08 设计（design）— 目录 + 翻页器

## 核心比喻
书放书架上，脑子不背全书，只背一张目录。要用哪章，按目录翻到那页读。

## 三块东西

### 1. 索引文件 rules_index.json（目录）
位置：`.workbuddy/rules/rules_index.json`
结构：一个 JSON 数组，每条规矩一项：
- id：编号（如 P06-1、W-6、S2-3）
- source：来源文件（六条/八条/个人三层哪个）
- title：标题
- summary：一句话它管啥
- when：什么时候该读它（触发场景关键词）
- layer：constant（常驻）/ ondemand（按需）

6 条的 layer 全 = constant；8 条和个人 14 条 = ondemand。

### 2. 查询器 rule_lens.py（翻页器）
位置：`.workbuddy/scripts/rule_lens.py`，Python 标准库，无依赖。
用法：
- `python rule_lens.py list` → 打印整张目录（编号+标题+一句话）
- `python rule_lens.py need "关键词"` → 按关键词匹配 when 字段，输出这次该读哪几条
- `python rule_lens.py need "关键词" --show` → 连规矩正文一起读出来（去对应文件里按行号抽）
- `python rule_lens.py check` → 自检：6 条是否仍常驻、索引是否覆盖了全部规矩

缓存友好设计：
- 输出开头永远是一段固定前缀（常量），写死"6 条铁律常驻"的提示，字字不变 → KV Cache 前缀命中。
- 按需命中的条目拼在后面。
- 同一输入 → 同一输出（排序固定、无时间戳、无随机）。

### 3. 加载开关（让 8 条和个人三层不常驻）
- 8 条：`项目工作规则.md` 的 frontmatter `alwaysApply: true` → `false`。两处目录（.workbuddy/rules 和 .codebuddy/rules）都改，保持逐字一致。正文不动。
- 6 条：`项目协作公约.md` 保持 `alwaysApply: true`，正文不动。
- 个人三层：在 SOUL.md 的 Standing Orders 里加一句指针——"完整三层按需读 .workbuddy/scripts/rule_lens.py need ..."，把第二层第三层的长条文从"每次全注入"改成"目录命中再读"。第一层 5 条（真铁律）保留常驻。

注意：SOUL.md 在用户目录，不进本项目 git；本单 on-demand 主体（索引、脚本、8 条开关）进 git。SOUL.md 的改动单独说明。

## 为什么这样缓存友好
KV Cache 复用的是"相同前缀"。我把每次都一样的那部分（6 条常驻提示 + 目录头）固定在输出最前面，变的部分放后面。这样每轮对话前缀一致，缓存能命中，不用重算。这是我能做的范围——真正的 KV Cache 在模型内核，我改不了。

## 风险
- 改 SOUL.md 需要小心不破坏其余内容，只加指针、把长条文标注为按需。
- alwaysApply 开关是否被平台真的遵守，需要下一轮新会话才能验证（本单只能验文件状态和脚本逻辑）。
