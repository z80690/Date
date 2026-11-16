# SDD 四步自检脚本 — 需求规格（spec.md）

- 版本：v1.0　日期：2026-11-16　状态：验证用最小真任务
- 目的：用一个真编码任务走通 SDD 四步，验证每步落盘、下游可追溯上游

## EARS 需求

- U1（Ubiquitous）：系统应当提供 `sdd_check.py`，检查一个 SDD 特性目录的四步产物是否齐全。
- E1（Event-driven）：当指定目录缺少 `spec.md` 时，系统应当报 FAIL 并指出缺第 1 步产物。
- E2（Event-driven）：当 `design.md` 缺失时，系统应当报 FAIL 并指出缺第 2 步产物。
- E3（Event-driven）：当 `tasks.md` 缺失时，系统应当报 FAIL 并指出缺第 3 步产物。
- E4（Event-driven）：当四份产物（spec/design/tasks + 执行记录）齐全时，系统应当报 PASS 并给出 4/4。
- S1（State-driven）：当目录路径不存在时，系统应当以非零退出码结束并说明原因。

## 验收标准

- AC1：`python sdd_check.py <完整目录>` 四步齐全 → 输出 PASS、4/4、exit 0。
- AC2：删掉任一产物 → 输出 FAIL、指出缺失步骤、exit 非 0。
- AC3：路径不存在 → exit 非 0 且给出明确提示。
- AC4：纯标准库，不装依赖；单文件 ≤ 500 行；函数 ≤ 30 行（项目硬棘轮）。

## 范围外

- 不校验产物内容对错（只验存在与非空），内容质量属人工门禁。
- 不做守护进程、不做轮询、不自动触发（公约第 5 条）。
