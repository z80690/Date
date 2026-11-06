# 首次提交清单（kb_arch_foundation，tasks 12.1）

> 逐文件列示，禁全量暂存。排除项：**.env（G3 拦截：含 CONTEXT7_API_KEY 与 SSH 公钥，已加 .gitignore 防护）**。建立：2026-11-07。

## 修改（8）

1. notes/知识库索引.md
2. notes/知识库维护机制.md
3. notes/项目事实表.md
4. .gitignore（追加 .env 防护行）
5. .codeartsdoer/rule/项目协作公约.mdc（平台写入 10 条规则=用户 2026-11-07 粘贴生效）
6. .codeartsdoer/rule/metadata.properties（同上，平台托管合法变更）
7. .codeartsdoer/skills/ProjectSkillStatus.txt（平台自动注册 review-code=true）
8. .codeartsdoer/experience-reuse/experiences/index.md（hook 增量）

## 新增（逐文件）

**notes/（5）**：
- notes/阶段状态机运行规则.md
- notes/注册表.md
- notes/复用评估表.md
- notes/学习成果-论文五篇.md
- notes/学习成果-项目五个.md

**skills/（2）**：
- .codeartsdoer/skills/review-code/SKILL.md
- .codeartsdoer/skills/review-code/scripts/review-code.ps1

**specs/kb_arch_foundation/（11）**：
- spec.md（v4）、design.md、tasks.md、st1-evidence.md、st2-materials.md、st2-exam-questions.md、st2-exam-key.md、st2-exam-answers.md、st2-exam-review.md、st3-design-report.md、规则草稿-永久生效.md

**经验库 hook 增量（经验资产，全部入库）**：
- experiences/agent-ops/ 下 8 个新文件（2026-11-06/07 系列：event-trigger-channel/independent-examiner/powershell-inline-json/precise-staging/tool-language-filter/background-long-task/learning-material-fidelity/refresh-env-baseline）
- experiences/build-env/ 下 2 个新文件（reference-repo-isolation/maven-download-degradation/windows-make-gate-fail）
- experiences/debugging/ 下 4 个新文件（curl-empty-response/git-commit-mojibake/github-api-vs-git/clone-timeout）
- experiences/workflow/ 下 17 个新文件（2026-11-06/07 系列，见 git status ?? 清单）
- experiences/testing/2026-11-07-framework-capability-verify-official-test-suite.md
- experiences/architecture/ 下 4 个新文件（integration-route/knowledge-base-tiered/oss-reference-pattern/process-control-state-machine/third-party-framework-model-config）
- reflect-reports/Date_2026-11-06.md

## 排除清单（附理由）

| 排除项 | 理由 |
|--------|------|
| .env | **G3 敏感拦截**：含 API 鉴权令牌与 SSH 密钥；已加 .gitignore 防护 |