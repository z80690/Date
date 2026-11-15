# Date 项目 · 长期约定

## Git 提交约定（2026-11-15 用户明令，本项目专用，覆盖用户级通用规则）

- **单分支 main**：不建 feature 分支、不切分支。当前只有 `main` + `origin/main`。
- **全量提交**：用户要"所有东西都提交、不留暂存区"。本项目提交用 `git add -A` 全量暂存（覆盖用户级"精确 git add、禁止 -A"的通用规则——仅限本项目）。
- **推送同步**：每次提交后 `git push origin main`。远程 `git@github.com:z80690/Date.git`，SSH 已认证，推送会同步更新关联的服务器。
- 提交前仍须核查无敏感文件（.env/密钥）和大文件，此条不覆盖。

## 功能隔离（2026-11-15 用户明令）

- WorkBuddy 与码道 CodeArts 严格隔离，不许混。
- WorkBuddy 配置/规则/技能/子智能体只在 `.workbuddy/`，运行时只读这里。
- `.codeartsdoer/` 是码道的，WorkBuddy 不读、不写、不依赖，仅作出处标注。

## 规则权威源（WorkBuddy 侧）

- `.workbuddy/rules/项目协作公约.md`（六条）+ `项目工作规则.md`（八条）为 WorkBuddy 侧唯一权威全文。
- 来源（`.codeartsdoer/rule/*.mdc`、项目根 `AGENTS`/`CLAUDE`）仅标注、非运行时依赖。
