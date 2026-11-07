# e2e 步骤1 建需求：特性进度速览脚本

> M4 全链路演练（tasks 5.1）｜ 步骤：1/4 建需求 ｜ 日期：2026-11-08
> 直读资源引用（spec 5.1 R3a）：规矩=公约.mdc（H1 注入）；记忆指针=项目事实表 §6；技能=**sdd-ref-distill（C1 主挂载调用）**+grill-me（评估后无需澄清）；编排=**sdd-spec-pipeline（C4）**。

## C1 调用留痕（sdd-ref-distill）

- 输入：sources=`.codeartsdoer/specs/sdd_agent_refactor/tasks.md` §8（M7 交付物清点）+`gates/m1-learn-gate.md`/`m2-exam-gate.md`/`m3-agent-gate.md`（三门禁已放行事实）+`notes/项目事实表.md` §6；goal=提炼"进度速览脚本应展示哪些信息"
- 蒸馏产出（三层）：
  - 主题：进度速览脚本应机械呈现"七门禁放行状态+五项交付物存在性"，供 M4 判定与 M7 清点复用
  - 要点：①M 链七门禁各以 gates/m<N>-*-gate.md 为证据（tasks 8.1 引用）②交付物五项=两智能体配置/exam 各轮四件套/compare-report/strip-checklist/migration-verify（tasks 8.1 清单）③判定须可重放（扫描输出留档原则，design §2.1.3-7 要素⑤）
  - 来源指针：tasks.md §8.1 行 449–460；design.md §2.1.3-7 五要素；三门禁文件（本特性 gates/ 目录）

## 需求条款（简化 EARS）

- R1：When 脚本运行，Where 在项目根执行，系统应扫描 `specs/sdd_agent_refactor/gates/` 目录，输出各门禁证据文件的存在性清单（m1–m7 逐项：存在/缺失）。
- R2：When 扫描完成，系统应输出能力迁移核验记录（migration-verify.md）与剥离扫描留档（m6-variant-scan.txt）的存在性专项行。
- R3：If 任一预期证据文件缺失，Then 对应行标注 MISSING 并以 exit 1 退出；全部预期文件存在则 exit 0。
- R4：输出格式为逐行纯文本（门禁号+文件名+状态），可留档可重放。

## 验收标准

1. 输出含 m1–m7 七行门禁状态+2 行专项文件状态；
2. 当前时点 m1/m2/m3 存在（PASS 行）、m4–m7 缺失（MISSING 行）→ exit 1（预期行为，因特性尚未推进到 M4 后门禁）——脚本须正确反映缺失而非报错崩溃；
3. 脚本经 review-code 调用（exit 语义生效）；
4. 四步顺序无跳步（本文件先于步骤 2–4 存在）。