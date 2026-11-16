# P07 专项验证轮次 — 答案与判分依据（p07_verify）

> 考教分离：本文件仅交付主智能体，禁混入 questions.md，禁向作答方/批改方泄露。

## 题 1　[记忆级]

答案要点：
- 第 1 步 → spec.md
- 第 2 步 → design.md
- 第 3 步 → tasks.md
- 第 4 步 → apply_record.md
（依据：design.md「产物清单映射」STEP_FILES 有序表；文件名与步骤号顺序须全对。）

判分依据：
- PASS：四个文件名全部正确，且步骤号顺序完全对应。
- PARTIAL：4 个文件名正确但顺序有局部错位；或步骤号 1–4 对应正确 3 项。
- FAIL：正确对应 ≤2 项，或把第 4 步产物误写为代码文件名（如 sdd_check.py）。

## 题 2　[理解级]

答案要点：
- (1) 输出逐项 FAIL：缺第 4 步 → `[MISS] 第4步`（并提示 apply_record.md），汇总 `FAIL 缺1项`；退出码 exit 1（非零）。（apply_record.md 实测已复现该分支。）
- (2) 目录本身存在且为目录，故不走"目录不存在/非目录 → exit 2"分支；四步未齐全（缺第 4 步产物），故不走"四项齐全 → PASS 4/4、exit 0"分支；命中"任一产物缺失/空 → exit 1"分支。
- (3) 承接 E4（四份产物齐全 → PASS、4/4）的反向语义：不齐则报 FAIL 并指出缺失步骤；按 STEP_FILES 有序表，缺失的是第 4 步产物 apply_record.md，故提示"缺第 4 步"。

判分依据：
- PASS：三小问均正确——输出 FAIL + 缺 1 项 + exit 1；(2) 说明目录存在→非 exit 2、未齐全→非 exit 0；(3) 答出 E4 反向 + 缺第 4 步。
- PARTIAL：退出码 exit 1 与 FAIL 判断正确，但 (2) 分支理由或 (3) EARS 条目/步骤号存在缺漏。
- FAIL：答成 PASS/exit 0 或 exit 2，或未识别出缺第 4 步产物。
