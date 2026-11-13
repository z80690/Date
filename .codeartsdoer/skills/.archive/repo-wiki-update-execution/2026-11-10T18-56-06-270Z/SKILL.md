---
name: repo-wiki-update-execution
description: >-
  repo-simple-wiki-update / repo-simple-wiki 技能在本机环境（Windows PowerShell 5.1 或
  WSL bash、纯 Markdown 知识库仓库）的执行适配契约：.md
  仓库符号骨架恒空降级为直读源文件；脚本参数契约（extract_changed_snippets 需文件路径非内联 JSON；bash=WSL
  时盘符路径须写 /mnt/c/）；subagent patch 漂移校验三形态（content≠new_content
  会静默丢修订正文、line_number_only 的 new_content 须为 JSON null 非 "null"
  字符串、直引号漂弯引号）；line_number_only 的 code_refs 以 wiki-index 原值为基线（subagent
  扩充未实读引用一律回退）；hash_status=changed 小节即使零改动也须走 merge 刷 source_hashes 否则永远无法 hash
  短路；工具运行时日志目录（.workbuddy 等）判成因 1 跳过；merge_section_patch 的覆盖盲区（H1 标题与
  frontmatter description 需人工补正）；progress.json 的 edit 边界陷阱（跨 stage
  块易吞相邻键名）；build_index 消费后删除 .code-links.json 属正常行为。凡执行 repo-simple-wiki-update
  / repo-simple-wiki 流程（含每日定时 Wiki 更新任务）、修订 codebase-knowledge/project-knowledge
  文档、或 Wiki 脚本报错时，应在主技能加载后、脚本执行前伴随加载本技能，预防性规避本机环境坑。
---

# repo-simple-wiki-update 执行适配契约（Windows PS5.1 / WSL bash + 纯文档仓库）

## 前置判定与核实
- 分支子目录：git 仓库用 `git rev-parse --abbrev-ref HEAD` 获取（本仓=master）；state.json 与 wiki 产物在 `.codeartsdoer/.codebase/branches/<分支>/` 下。glob 模式 `.codeartsdoer/**` 可能因点前缀目录被忽略而返回空——动笔前用递归 `Get-ChildItem -Force -Recurse` 实查目录真实内容，勿凭 glob 空结果断言"产物不存在"（2026-11-08 实证：glob 报空但 branches/master/docs 下 7 篇文档齐全）。
- 纯 .md 仓库（无代码文件）：extract_symbols.py 不支持 .md 扩展名 → 骨架文件生成但为空（status=warning, symbols=0），属预期而非故障。跳过符号骨架环节，subagent prompt 直接给变更源文件实文与定位摘要；阶段 2.5（切片）恒跳过（常规档）。
- architecture.json 的 `modules=[]` 表示无新模块判定依据；temp/ 等临时目录按"不在 Wiki 关注层面"处理，判定依据对照项目事实表的入库排除清单（temp/ 在排除项中）。
- 工具运行时日志目录（如 `.workbuddy/memory/automations/` 的自动化签到执行记录）即使被 git 跟踪并出现在 state.json 的 changed_files 中，也判成因 1（不在 Wiki 关注层面）跳过：不属于治理机制/协作规范/业务术语任何关注层面，且 wiki-index 零引用；判定结论写入 update_plan.unmatched_files 的 judgment/reason 字段留痕（2026-11-09 实证：WorkBuddy 签到日志，实读确认后过滤）。
- 同一变更集跨轮重复（version_token 187→198 两轮 changed_files 均为 .workbuddy 日志+notes/项目事实表.md）：上轮 progress.json 的 filter_note 与 update_plan 成因判定可沿用作先验，实读复核文件现状仍属同一性质即可快速判定，无需重新全量分析；先验不成立时以实读为准（2026-11-09 实证：token 198 轮沿用 187 轮 .workbuddy 成因 1 判定，实读复核后过滤）。

## 脚本参数契约
- extract_changed_snippets.py 的 `--changed-files` 必须传 **JSON 文件路径**（脚本内部 `open()` 读取），传内联 JSON 字符串报 FileNotFoundError。变更列表先 write 落盘成 json 文件再传（如 `.codeartsdoer/temp/changed_files.json`）。
- **bash 工具实为 WSL 的会话**（命令输出带 `wsl:` 前缀警告即是）：`_wiki_cmd.sh` 内的 Windows 盘符路径必须写成 `/mnt/c/...`——`cd C:/Users/...` 报 "No such file or directory" 且整条链 `|| exit 1` 提前终止；相对路径（从仓库根出发）不受影响。此场景校验链用 .sh（每行一条命令，勿用续行符），勿沿用 .ps1 写法（2026-11-08 实证：首条命令 `cd C:/` 失败，改 `/mnt/c/` 后 reverse_lookup 正常；2026-11-09 两次实证：脚本内路径变量用 `/c/Users/...`、或参数位置直接写 `C:/...`——后者被 WSL python 相对拼成 `/mnt/c/<workdir>/C:/Users/...` 后报 can't open file——均改 `/mnt/c/` 前缀后全部通过）。
- modified 文件的变更行更直接的做法：`git diff -U6 -- <文件>`（若已提交则 diff 无输出，此时以当前文件实文与 wiki-index 现有记录对照得出新旧差异）。
- merge_section_patch.py：.code-links.json 不存在时自动创建，无需预建。

## subagent patch 流程
- subagent 把 patch JSON **写到文件**（`.codeartsdoer/temp/wiki-patches/<name>.json`，UTF-8 无 BOM）而非粘在返回消息里，防长 JSON 被截断；返回只带文件路径+各小节 action 决策摘要。
- subagent prompt 必须自包含：受影响小节当前原文、变更对照材料（新旧内容/新增文件清单与定位）、模板小节字数规范（架构设计 ≤300 字、其他每节 ≤200 字）、section_title 必须逐字复制 `## ` 后标题、code_refs 行号须实读源文件核实；主 Agent 可在 prompt 中附各小节的同层面预判（基于已读材料），但 action 最终决策要求 subagent 自行判断并为其预判负责。
- **主 Agent 落盘 patch 前必校验三处漂移**：①字段名——subagent 可能返回 `content` 而非规范要求的 `new_content`，而 merge_section_patch.py 只读 `p["new_content"]`，缺失时该小节会**静默按 line_number_only 处理、修订正文无声丢失**（不报错），落盘前统一改回 `new_content`；②引号——subagent 可能把原文直引号 `"..."` 漂移成弯引号 `“...”`，落盘时还原为原文风格；③null 字面量——line_number_only 的 `new_content` 必须是 JSON null，subagent 可能返回字符串 `"null"`，落盘前改回 null（2026-11-08 实证：4 个 subagent 中 2 个字段名漂移、1 个引号漂移；2026-11-09 实证：line_number_only 返回 "null" 字符串；均因落盘前校验而零损失）。
- **line_number_only 的 code_refs 以 wiki-index 原值为基线**：先实读核对原引用行号是否仍准确，准确则维持原值。subagent 常把同文档其他小节的引用复制进来造成扩充——未实读支撑的引用一律裁剪回退，避免污染 source_hashes 基线（2026-11-09 实证：概述小节原 2 ref 被 subagent 扩成 4 ref，回退后 merge 通过）。同数量的行号**替换**（非扩充）若新行号有实文对应表述支撑（每个 ref 能指认正文中对应句），可接受（2026-11-09 实证：架构设计 refs :22/:24 被 subagent 实读后替换为 :21/:55，分别对应「仲裁顺序」与「写者约束」表述，采纳后 validate 2/2 通过）。
- **hash_status=changed 的小节即使正文不改、行号不变也必须输出 patch 走 merge_section_patch**：source_hashes 只在 merge 时刷新；不发 patch 则下次 reverse_lookup 对该小节永远报 changed、无法进入 hash 短路，每轮增量都重复修订同一批小节（2026-11-09 实证：merge 输出 hashes_updated 确认事实表新 hash 已写入索引）。
- **merge 覆盖盲区**：merge_section_patch.py 只处理 `## 小节`，H1 标题与 frontmatter description 不在 patch 范围。若模块定位已变（如 notes 模块从 1 篇扩为 16 篇），主 Agent 需手动 edit 这两处，否则 build_index 从 description 提取的 title 会继续传播旧口径。

## 校验与索引
- 校验链写进单个 .ps1 顺序执行：merge_section_patch ×N → validate_code_links(--wiki-root docs) → lint_wiki → redact_secrets --check。
- lint_wiki 的 orphan-page-candidate warning 若为全量生成即存在的全库遗留（无 [[module_id]] 双链），记入报告不阻塞；error 才需处理。
- build_index.py `--wiki-root <docs> --code-repo-root <repo> --language zh`：输出"已删除 N 个 .code-links.json"属正常（先消费后删除，非数据丢失）；更新/复用统计即增量生效证据；overview.md 与 WikiRetrieval.md 由其自动再生，读回验证 title/统计行是否反映修订。
- 收尾：progress.json 逐 batch 落盘（stage_3/4 的 pending→completed 移转在 merge+validate 通过后立即写，防中断丢失）；临时脚本用完删除，patch JSON 留 temp/patches/ 追溯（temp/ 为入库排除区）。
- **edit 改 progress.json 的边界陷阱**：oldString/newString 必须限制在单个 stage 块内部，勿跨 stage 边界——跨块时易出现 oldString 含相邻 stage 的开头键名行而 newString 忘带该行，导致 `"stage_4": {` 之类键名被吞、JSON 损坏（2026-11-08 实证，读回核实后修复）。跨块/大面积改写优先整体 write 并完整保留 module_tree；每次改完用 `python -c "import json; json.load(open(path, encoding='utf-8'))"` 验证合法性再进下一阶段。
- **skill_manage 修改生成技能的通道差异**：edit 校验器按行解析 frontmatter，遇 `description: >-` 折叠样式会误报 "SKILL.md must have name and description in frontmatter" 而拒绝（frontmatter 实际完好）；patch 与 patch_frontmatter 的校验路径可正常处理该样式。改正文用 **patch**，改 frontmatter 用 **patch_frontmatter**，write_file 不能写 SKILL.md 本身（subpath 仅限 references/examples/scripts/assets）（2026-11-09 实证：edit 连续 4 次全拒，换 patch 全部通过）。
