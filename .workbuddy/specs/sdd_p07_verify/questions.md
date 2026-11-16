# P07 专项验证轮次 — 考核题目（p07_verify）

- 轮次标识：p07_verify
- 知识域：SDD 四步（spec.md → design.md → tasks.md → 按 tasks 执行）
- 题量：2 道（派工单覆盖默认 50）
- 认知层级：记忆级 / 理解级（派工单覆盖默认三级要求）
- 命题范围：仅出自已三查材料 `.workbuddy/specs/sdd_four_step_selfcheck/` 下 spec.md、design.md、tasks.md、apply_record.md
- 说明：本文件仅含题目，不含答案；答案要点与判分依据见 key.md（考教分离）

## 题 1　[记忆级]

`design.md` 的实现设计中定义了一张名为 `STEP_FILES` 的有序表，把 SDD 四步映射到要检查的产物文件名。请按第 1 步到第 4 步的顺序，写出这张有序表中每一步对应的产物文件名。

## 题 2　[理解级]

现有一个存在的目录，其中只有三份非空文件：`spec.md`、`design.md`、`tasks.md`，缺少 `apply_record.md`。依据 `design.md` 的退出码设计与 `spec.md` 的 EARS 需求，回答：

1. 运行 `python sdd_check.py <该目录>` 会输出哪些关键信息、以什么退出码结束？
2. 为什么走这个分支，而不是"目录不存在"的分支或"四步齐全"的分支？
3. 这个场景承接了哪条 EARS 需求的反向语义，缺失提示会指出缺第几步产物？
