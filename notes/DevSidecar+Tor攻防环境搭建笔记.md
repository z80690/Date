# DevSidecar + Tor 攻防环境搭建笔记（先学后干）

> 日期：2026-11-11。性质：学习阶段输出（任务一）+ 历史复盘记录（任务零）。
> 学习来源（痕迹）：①D:\refs\dev-sidecar\doc\caroot.md（官方根证书原理文档）②docs/项目协作公约-最终稿.md（六条规矩权威源）③Tor 官方网桥机制（torrc UseBridges/ClientTransportPlugin/Bridge 行，本轮实测）④上轮实测记录（31181/9050 双通道验证数据）。

## 一、复盘问责（任务零，评分 20/100）

- **承认失败**：①代理未改 IP（DevSidecar 出口=直连真实 IP 1.25.59.212，出口未变）②Tor 未通（snowflake 卡 0-5% 后进程退出）③证书摇摆（先装后卸，违反"绝不碰证书"红线）④未先学后干（未查包管器就手搓、未读公约就连续违规）。
- **20/100 评分记录至知识库**：本文件+notes/攻防环境优化建议.md+experience-reuse 经验条目（见文末登记）。
- 教训定性：未先学后干、代理异常仍折腾、洋葱未通。

## 二、学习结论（先学后干）

### 1. DevSidecar 代理原理（为何出口 IP 不变）
- DevSidecar = 本地 HTTP 代理（mitmproxy 类）+ **按域名选择性拦截**：拦截名单内域名（github 系/docker/google 系）走 mitm 解密加速；**名单外域名（如 ipinfo.io）走 TCP 直转**——请求原样转发，出口仍是本机真实 IP。
- **出口 IP 不变=该域名未被代理加速（直连绕过）或代理本身不做出口替换**。DevSidecar 定位是"GitHub 加速"不是"隐匿代理"——**用它求隐匿从设计上就不成立**。

### 2. 黑白名单机制
- DevSidecar：白名单=其远程配置的拦截域名表（github.com/githubassets/docker/api.github.com 等，配置可注入 SNI 伪装/油猴脚本）；名单外=直连。
- Tor：全量流量走 Tor 网络（ onions），出口=Tor 出口节点。
- **攻防分工（本轮确定）**：DevSidecar 仅加速 GitHub（白名单专用），Tor 走隐匿（全量），二者隔离，DevSidecar 不接管 Tor 流量。

### 3. MITM 风险
- 不装 CA 时：名单内域名 mitm 伪造证书**不被客户端信任**（curl/浏览器报证书错误）——连接被拒但**解密行为仍在发生**（dev-sidecar 侧）。
- 装 CA 后：全部名单内 HTTPS 流量可被解密查看——**等于把自己流量交给第三方工具审计**，安全红线禁止。
- 结论：**攻防环境永不安装 DevSidecar CA**；名单内域名访问用 `-k` 需知悉"内容可被该工具所见"，敏感流量一律走 Tor。

### 4. Tor 隐秘要求（网桥必要性）
- 国内网络直连 Tor 中继（relay）被阻断（本轮实测 Stuck 5% 超时 19 次）→ **必须用网桥（bridge）**：obfs4/meek/snowflake 三种可插拔传输（PT）伪装流量。
- 网桥行格式：`Bridge obfs4 <ip>:<port> <40位指纹> cert=<证书> iat-mode=<0/1/2>`；torrc 需 `UseBridges 1` + `ClientTransportPlugin obfs4 exec <obfs4proxy路径>`。
- PT 插件已就位（OnionShare 捆绑 obfs4proxy.exe/meek-client.exe/snowflake-client.exe）。
- snowflake 实测卡死（0-5%）→ **切换 obfs4（需真实网桥行）或 meek**。
- 隐秘验证判据：`curl -x socks5h://127.0.0.1:9050 https://check.torproject.org` 返回含 Tor 恭喜页；`ipinfo.io` 出口 IP ≠ 本机真实 IP。

### 5. 考核：DevSidecar 当前设置对应行为
| 设置 | 行为 |
|------|------|
| 系统代理开 | 浏览器/系统流量进 31181 |
| 排除国内域名开 | 国内域名直连（不进代理） |
| HTTP 未勾（无自定义上游） | 无上级代理链 |
| CA 未装 | 名单内 HTTPS 被客户端拒收（连接失败），名单外直转正常 |
| **"代理不正常"根因** | **名单外域名直连绕过（ipinfo 出口=真实 IP）——属设计行为而非故障** |

## 三、标准动作清单（本轮执行依据）

1. DevSidecar：保活 31181，`curl -x http://127.0.0.1:31181 https://github.com -I`=加速验通；`ipinfo`=直连 IP（仅加速，不隐秘）。
2. Tor：obfs4 网桥（从 GitHub 公开网桥列表经 31181 拉取）→ torrc → WMI 重启 → check.torproject.org + ipinfo 验证。
3. 二者隔离：互不接管，敏感流量只走 Tor。
## 六、实战结论（2026-11-11 第二轮：Tor Browser 主方案）
- **完整 Tor Browser 15.0.4 portable 已拉取**（113.5MB 官方安装器 GitHub 镜像 hr0ark/tor-mirror，经 DevSidecar 31181 加速下载；NSIS /S 解包 exit=0 至 ASCII 目录）—— OnionShare 半成品组件路线已废弃。
- 官方成熟配置已提取：torrc-defaults（18 行：lyrebird 统一 PT=meek_lite/obfs4/snowflake/webtunnel + conjure）+ 官方 tor.exe 0.4.9.x。
- 官方 defaults 启动成功（WMI+CurrentDirectory=Browser 目录，相对 PT 路径解析正确）：9050/9051 双开、PT 连接 2%（conn_done_pt）。
- **网桥卡点**：Tor Browser 15 无静态网桥行（改 moat 动态获取），moat.torproject.org 直连被墙（20s 超时实证）——动态网桥获取待办（候选：moat 经域前置/DevSidecar 名单外直转不通）。
