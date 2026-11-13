---
id: 2026-11-13-dumpcap-hard-kill-buffer-loss-pcap-missing
title: "dumpcap 等需 flush 子进程禁用 terminate 硬杀：CTRL_BREAK_EVENT 优雅停止防 pcap 假性丢失"
category: debugging
nature: pitfall
created_at: 2026-11-13T12:33:44
updated_at: 2026-11-13T12:33:44
tags: [dumpcap, subprocess, pcapng, 进程终止, 写缓冲]
keywords: [terminate 等价 TerminateProcess 硬杀, pcap file missing at stop, E_CAPTURE_BROKEN, CREATE_NEW_PROCESS_GROUP, CTRL_BREAK_EVENT, 优雅停止, 写缓冲未 flush, 证据链断裂假象, wait 超时兜底, import signal]
problem_patterns: [subprocess.terminate() 硬杀长驻记录型子进程，缓冲数据未落盘即死亡，产物文件不存在或为 0 字节，误判为"采集失败"而非"终止方式错误", 停止后产物缺失反复重跑采集，浪费轮次且证据链断裂假象持续复现]
source_sessions: [ses_e2d1b45edffeiZTF0xjq1cyv7a]
project: Date
severity: medium
quality_score: 90
hit_count: 0
last_hit_at: null
low_quality_hit_count: 0
tier: S
related_experiences: [2026-11-13-pytest-sessionfinish-winerror5-cleanup-noise, 2026-11-13-restricted-agent-adapter-literal-ip-jsonl-verdict]
---

# dumpcap 等需 flush 子进程禁用 terminate 硬杀：CTRL_BREAK_EVENT 优雅停止防 pcap 假性丢失

## Scenario

Python 编排 dumpcap 抓包会话（`dumpcap -i <iface> -w out.pcapng` 长驻运行，演练步骤结束后 stop）。用 `Popen.terminate()` 停止后，会话管理器校验产物时报 `pcap file missing at stop`（自定义错误码 E_CAPTURE_BROKEN），目录里只有步骤文本文件、pcapng 完全不存在，且 dumpcap 进程已消失。表象是"抓包采集失败"，实际采集本身在正常进行。

## Key Signals

- **误导表象**：stop 后产物文件缺失 → 直觉归因"dumpcap 没写文件/权限问题/接口选错"，倾向重跑采集或换接口。
- **关键判别信号**：采集期间进程一直存活（start 返回正常、无 stderr 输出）；唯独 stop 动作之后产物消失——问题被"停止"这个动作本身触发。
- **机制**：Windows 上 `subprocess.terminate()` 调用 `TerminateProcess`，是無通知硬杀；dumpcap 的环形写缓冲尚未 flush 到 pcapng 即死亡，已抓数据随进程蒸发。

## Essence

对**持续写盘的记录型子进程**（抓包/日志/审计流），终止方式决定产物完整性：硬杀 = 缓冲丢失 = 产物假性缺失。因果链：terminate() → TerminateProcess 无通知强杀 → dumpcap 写缓冲未 flush → pcapng 从未落盘 → 校验器报 missing。修复不是"重试采集"，而是给子进程一个优雅退出通道：Windows 控制台进程可接收 `CTRL_BREAK_EVENT` 触发其内部信号处理（dumpcap 收到后正常关闭文件句柄并 flush），Python 侧 `creationflags=CREATE_NEW_PROCESS_GROUP` 是发送该信号的前提（否则目标不在可_signal 的进程组内）。

## Approach

1. **启动时加入新进程组**：
   ```python
   proc = subprocess.Popen(
       [dumpcap, "-i", iface, "-w", str(pcap)],
       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
       creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,  # Windows
   )
   ```
2. **停止时优雅信号 + 超时兜底**：
   ```python
   import signal
   proc.send_signal(signal.CTRL_BREAK_EVENT)   # 触发 dumpcap 正常 flush 退出
   try:
       proc.wait(timeout=15)
   except subprocess.TimeoutExpired:
       proc.terminate()                        # 兜底，仅在优雅停止失败时硬杀
   ```
3. **校验产物而非进程**：stop 成功的判据是 pcapng 文件存在且非空（contiguous 标志），不是"进程已退出"。
4. **失败分支留痕**：优雅停止后仍无产物 → 才是真正的采集故障（权限/接口/驱动），此时按采集故障排查，而非终止方式问题。

## Faster Next Time

- 写任何"长驻记录型子进程"的 stop 逻辑时，默认套用"CREATE_NEW_PROCESS_GROUP 启动 + CTRL_BREAK_EVENT 停止 + wait 超时兜底 terminate"三件套，`import signal` 别忘（CTRL_BREAK_EVENT 在 signal 模块）。
- 更早发现：单测加一条——start 后立即 stop，断言产物文件存在；硬杀路径在此用例必挂。
- 判别口诀：**"产物只在 stop 后消失 = 终止方式问题；采集期间就无产物 = 采集本身问题"**。

## Applicability Boundaries

- 适用：Windows + Python subprocess 管理长驻记录型进程（dumpcap/tshark/tcpdump 类抓包、日志采集器、审计流写出器）。`CTRL_BREAK_EVENT` 是 Windows 控制台专属，POSIX 对应 `SIGINT`/`SIGTERM` 优雅路径。
- 不适用：一次性短命令（无缓冲积累问题）；目标进程不处理控制台事件的（CTRL_BREAK 无效，需查该进程的退出机制或改用其自带 stop 命令/管理端点）；产物由外部转储（如内核环形缓冲另行导出）的场景。
- 边界：`send_signal(CTRL_BREAK_EVENT)` 对未加 CREATE_NEW_PROCESS_GROUP 启动的进程会报错或误伤同组进程——启动与停止两处必须配套。

## Evidence or Examples

- 实证会话（P003 本地攻防演练 round-07）：`capture_session("stop")` 抛 `E_CAPTURE_BROKEN: round evidence invalid: pcap file missing at stop`；round 目录仅含 step-01-traffic.txt/step-02-heartbeats.txt，pcapng 缺失，dumpcap 进程清单为空。
- 修复后 round-08 同型流程：`capture stop → pcap=...round-08.pcapng contiguous=True`，随后 tshark 对该 pcapng 完成完整 J1~J5 判定——产物链闭合。
- 修复 diff 要点：capture.py `_start` 增 `creationflags=subprocess.CREATE_NEW_PROCESS_GROUP`；`_stop` 由 `terminate()+wait` 改为 `send_signal(signal.CTRL_BREAK_EVENT)+wait(15s)+超时兜底 terminate`；文件头补 `import signal`。