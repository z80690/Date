# 派工单（apply 预演 · 真实任务）

> 本单不是示范样例，是 G4.1 用真实改动跑出来的执行记录。
> 派工时刻：2026-11-26 21:00；验收回填：2026-11-26 21:03。
> 依据模板：`.workbuddy/templates/派工单模板.md` v1.1。

## 1. 基本信息

- 派工日期：2026-11-26
- 特性名：sdd-dual-mode
- 本步产物：`apply`
- 模式：sdd — 由 `sdd_mode_gate.py` 判定，exit=0（关键词命中"实现"、"配置"）
- 任务描述（原话）："tasks 通过。进 G4 预演，派工单六节全填贴真输出，人工扫签收别省。archive 和 commit 仍等我单独授权。设计细节你定，我只偶发纠偏。"
- 真实改动内容：给 `sdd_artifact_gate.py` 补 `apply` 产物类型（模板写"四选一含 apply"但门禁只认三种，是真缺口）；模板升 v1.1；门禁用法提示改为按配置取类型。
- 授权边界：archive / git commit 属高风险动作，本单不碰，等用户单独授权。

## 2. 门禁命令（必填，不许留空）

```bash
# 模式门禁
python .workbuddy/scripts/sdd_mode_gate.py "实现 sdd_artifact_gate.py 的 apply 产物门禁支持，配置派工单模板 v1.1"
# 期望 exit: 0=sdd / 1=web-coding / 2=问用户

# 产物门禁（本步产物 apply）
python .workbuddy/scripts/sdd_artifact_gate.py apply log/2026-11-26-sdd-dual-mode/apply_预演派工单.md
# 期望 exit: 0（六节齐 + 字数>=1500 + 人工扫已签收）

# CLI 语义门禁（change 四件齐后）
openspec validate sdd-dual-mode --strict --json
# 期望 exit: 0
```

## 3. 门禁输出回执（必填，贴真实输出）

模式门禁真实 stdout：

```
{"mode": "sdd", "exit": 0, "sdd_hits": ["实现", "配置"], "web_hits": [], "default": "sdd"}
```

exit=0。

产物门禁真实 stdout（首次运行，2026-11-26 21:03）：

```
[PASS] apply log/2026-11-26-sdd-dual-mode/apply_预演派工单.md 章节齐( 6 ) 字数 2590 人工扫已签收
```

exit=0。此为 21:03 首次运行真输出；回填后的定稿复跑见本文件末尾「最终复跑」及运行时报告 §2.8。

CLI 语义门禁真实 stdout：

```
{
  "items": [
    {
      "id": "sdd-dual-mode",
      "type": "change",
      "valid": true,
      "issues": [],
      "durationMs": 75
    }
  ],
  "summary": {
    "totals": {
      "items": 1,
      "passed": 1,
      "failed": 0
    }
  },
  "version": "1.0"
}
```

exit=0，1/1 passed。

补充真输出（同一轮另一次模式门禁，用用户原话直贴）：

```
{"mode": "need-clarify", "exit": 2, "sdd_hits": [], "web_hits": [], "default": "sdd"}
```

exit=2。这是盲区证据：门禁只认字面关键词，识别不了"预演/派工单六节"这类流程内元任务。按 `sdd_modes.json` 决策规则第 5 条（用户已授权"设计细节你定"）自决走 sdd，但盲区本身回写进模板 v1.1 修订说明，不靠我临场判断消化掉。

## 4. 内容偏差人工扫（必填）

- 扫人：**用户正式签收，2026-11-26 21:11**。此前 21:03 的助手自检只作预演留痕，不顶替用户签字。
- 用户签收原话："G4 预演通过，派工单 §4 人工扫由我签收：六节填全、真输出贴齐（含失败 exit=2）、apply 门禁 PASS、负向真拦、报告烂账已清，没偷跑 archive/commit。进 G5 收尾同步，archive 和 git commit 仍等我单独授权。设计细节你定，我只偶发纠偏。"
- 用户逐项核对六条：
  1. 六节填全 — 认可
  2. 真输出贴齐（含失败 exit=2）— 认可
  3. apply 门禁 PASS — 认可
  4. 负向真拦 — 认可
  5. 报告烂账已清 — 认可
  6. 没偷跑 archive/commit — 认可
- 结论：**无偏差，G4 通过**（用户裁决，21:11）。

### 历史留痕：助手预演自检（21:03，已被上面的用户签收取代）

1. 字段对不对：六节标题与 `sdd_modes.json` 的 `apply.required_sections` 一一对上，没有"写了但门禁不认"的字段。
2. 输出真不真：三条 stdout 均为 Bash 实跑回显，含 exit code；exit=2 的失败输出也照贴，没挑好的贴。
3. 授权边界：archive / commit 没碰；自检时没让自己冒充用户签字。
- 自检结论：无偏差（预演范围内）。遗留项模式门禁元任务盲区已回写模板，不作为本单偏差。

## 5. 产物路径

- 落盘路径：`log/2026-11-26-sdd-dual-mode/apply_预演派工单.md`
- 文件存在且非空：`ls -la` 输出贴这里：

```
-rw-r--r-- 1 Administrator 197121 4438 Nov 26 21:02 log/2026-11-26-sdd-dual-mode/apply_预演派工单.md
```

## 6. 推进判定

- [x] 所有门禁 exit 0（模式 0 / 产物 0 / CLI 0；exit=2 那次为盲区暴露，已自决+回写，非本单门禁失败）
- [x] 门禁输出已贴（非"已通过"占位，含真实 JSON 与 exit code）
- [x] 人工扫已签收（**用户 21:11 正式签收，六条逐项认可**；助手预演自检留痕见 §4）
- [x] 产物文件存在非空（回填后 `ls -la` 实证）

四勾全中，用户 21:11 裁决 G4 通过。G4 关闭，进 G5 收尾同步；archive / commit 仍属高风险动作，等用户单独授权，本单不碰。

## 最终复跑（回填后，2026-11-26 21:05）

产物门禁重跑输出（贴入本段之前的定稿状态）：

```
[PASS] apply log/2026-11-26-sdd-dual-mode/apply_预演派工单.md 章节齐( 6 ) 字数 2676 人工扫已签收
```

exit=0。

`grep -c '^## '` = 7：六节 + 本段「最终复跑」，多出的这个是证据段，不是第七个字段；模板实物仍是 6 节（`grep -c '^## ' .workbuddy/templates/派工单模板.md` = 6）。

自指说明：本段贴入后文件字数再增至约 2800，但门禁判据（六节齐 + 字数≥1500 + 人工扫标记在）不受字数增长影响；本轮最终一次运行结果以运行时报告 §2.9.3 / §2.10 为准。不无限递归贴输出。

21:11 用户正式签收：§4 扩写为"用户六条逐项认可 + 助手自检历史留痕"，文件字数再增；门禁判据不变，G5 收尾复跑的真实输出记在运行时报告 §2.10。
