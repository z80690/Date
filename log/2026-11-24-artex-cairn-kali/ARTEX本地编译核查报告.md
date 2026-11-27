# ARTEX 本地编译核查报告（用户派工三步 + 成本测算）

- 时间：2026-11-24｜位置：Windows 端（用户只能查 Windows）
- 触发：用户指出"D 盘那份是 Go 源码，直接编译不用 Docker"，派三件事 + 成本测算，要求"做不到指到文件、指到报错，别说环境不足四个字"
- 框架：**ARTEX 本体**（`D:\refs\ARTEX` 源码 + `D:\refs\ARTEX-release\artex-0.3.29-windows-amd64` 二进制），不是 Cairn

---

## 第一件：数据库到底要什么、填哪几项；Go 要哪个版本

### 数据库：只要 PostgreSQL，没有 SQLite 退路

| 项 | 实据（文件:行） |
|---|---|
| 只用 PG | `db/db.go:1` 注释："Package db is the PostgreSQL data source for ARTEX (取代旧 graph 单文件 SQLite)"；`db/db.go:17` 用 `pgx/v5/stdlib` 驱动 |
| 无 SQLite 后端 | `cmd/artex/main.go:1` 注释还残留旧的"dual SQLite graph stores"，但实际 `NewManager` 走 PG；**注释过期，代码是 PG** |
| DSN 解析优先级 | `config/config.go:129-148`：① 环境变量 `ARTEX_PG_DSN` ② `config.json` 的 `database.dsn` ③ `database` 分字段 host/port/user/password/dbname/sslmode 组装 |
| 自动建库 | `db/db.go:100-131` `ensureDatabase`：连 `postgres` 维护库，目标库不存在会自动 CREATE（所以只需 PG 服务起、账号有建库权） |

### 要填哪几项（你现在的 `config.json` 已经够了）

现有实际内容（密码是上次演练设的本地值）：
```json
{
  "database": {
    "dsn": "postgres://artex:artex-local-drill-2026@127.0.0.1:5432/artex?sslmode=disable"
  },
  "skill_dir": ""
}
```
- **这一项 dsn 就够了**，不用再填别的。用 PG 官网安装包装完后：创建用户 `artex` / 密码 `artex-local-drill-2026` / 库 `artex`（或让程序自动建），改端口/密码时同步改这行即可。
- LLM 配置项（`.env.example:9-15`，Key 全部留空 = 按要求去模型配置）：
  ```
  ANTHROPIC_API_KEY=        ← 留空
  OPENAI_API_KEY=           ← 留空
  ARTEX_LLM_PROVIDER=       ← 填 openai（走 OpenAI 兼容格式）
  ARTEX_LLM_MODEL=          ← 填模型名
  ARTEX_LLM_BASE_URL=http://127.0.0.1:7810/v1   ← 上次 run-p003.bat 就是这么写的
  ARTEX_LLM_PROXY=          ← 留空（直连、不继承系统代理，llmhttp/client.go:10）
  ```

### Go 版本

- `go.mod:3`：`go 1.26.10`（编译需要的最低版本）

---

## 第二件：go version（有没有 Go、要装哪个多大）

```
$ go version
go version go1.26.5 windows/amd64
```

- **本机有 Go：1.26.5**。比 go.mod 要求的 1.26.10 低一个小版本。
- Go 1.26.x 系列是同一大版本，小版本差 5 个 patch。**需不需要升级看第三件 build 实测**——若 build 因版本检查报错，就升级到 1.26.10（约 70MB 安装包）；若不报版本错，1.26.5 可直接编译。
- Go 安装位置：`D:\soft\go`，模块缓存 `D:\soft\go\pkg\mod`，代理 `https://goproxy.cn,direct`。

---

## 第三件：go build 试一次，报错原样贴

命令（在 `D:\refs\ARTEX` 下）：
```
go build -o /tmp/artex-build-test.exe ./cmd/artex
```

首次执行（前台，120 秒超时）被工具 SIGTERM 中断，无文本输出——原因是首次编译要拉几十个依赖模块，超过 120 秒。

第二次（后台任务持久跑，输出重定向到 `D:\refs\ARTEX\build-attempt.log`）：
```
cd /d/refs/ARTEX && go build -o /tmp/artex-build-test.exe ./cmd/artex > build-attempt.log 2>&1; echo "EXIT=$?" >> build-attempt.log
```

**最终原始日志**（`build-attempt.log` 全部内容，一字不改）：
```
EXIT=0
```

**零报错，编译成功。** 产物 `/tmp/artex-build-test.exe`，46,601,728 字节，生成时间 02:51。首次前台那次 SIGTERM 只是 120 秒超时，不是编译失败。

二进制冒烟测试（`-h` 原始输出）：
```
Usage of C:\Users\ADMINI~1\AppData\Local\Temp\artex-build-test.exe:
  -addr string
    	HTTP listen address (default ":8787")
  -data string
    	data directory for SQLite stores (default: data/ next to the executable) (default "data")
  -proxy string
    	traffic recording proxy address (empty to disable) (default "127.0.0.1:8788")
```

> 结论：**不需要升级 Go**。go1.26.5 能编译 go.mod 声明 1.26.10 的源码（Go 的小版本差异不触发 go.mod 版本检查拒绝）。不用 Docker、不装新软件，ARTEX 源码本机可直接编译成 Windows exe。

---

## 第四件：跑通一次大概烧多少钱（帮你决定接哪个模型）

### 测算依据（不是拍脑袋）

- ARTEX 默认预算：内置 agent `run_seconds=1200`（单次 run 墙钟 20 分钟，`db.go:224` COALESCE(...1200)）；`max_turns=0`（不限轮，`schema.sql:806`）；并发 worker 默认 3（README:317）。
- 一次**本地小规模靶场演练**（单目标、planner+3worker、约 50~200 轮 LLM 调用）取中位：**输入 2M token、输出 0.4M token**（输出单价通常是输入 3~5 倍，这是 token 成本的大头）。
- 价格来源：DeepSeek 官方 rate card（api-docs.deepseek.com）、Anthropic/Claude 官方定价 2026-11 口径、第三方比价站交叉（llm.anotherwrapper.com 2026-11-23、deepseek.ai 2026-07-25）。

### 一次演练成本表（2M in / 0.4M out）

| 模型 | 单价(输入/输出, 每1M) | 一次演练成本 | 折人民币(≈7.2) |
|---|---|---|---|
| DeepSeek V4-Flash | $0.15 / $0.60 | **$0.54** | ≈¥3.9 |
| DeepSeek V3（70%缓存命中） | $0.07~0.27 / $1.10 | **$0.70** | ≈¥5.0 |
| DeepSeek V3（无缓存） | $0.27 / $1.10 | $0.98 | ≈¥7.1 |
| DeepSeek R1（推理） | $0.55 / $2.19 | $1.98 | ≈¥14.2 |
| GPT-5.4 | $2.50 / $15.00 | $11.00 | ≈¥79 |
| Claude Sonnet 4.5 | $3.00 / $15.00 | $12.00 | ≈¥86 |

**结论**：本地演练这种量级，DeepSeek V3/Flash 一次几块钱人民币；Claude/GPT 一次 80 块左右，差 15~20 倍。真按 FBI 通报那种"23 小时、140 fact"的全规模攻击，token 量再乘几十倍，模型选择就是几百 vs 几万的区别。**对咱们本地靶场，DeepSeek V3 性价比最高**；ARTEX 的 FBI 通报也提到攻击者实例多用 DeepSeek Flash 系（我只引用通报口径）。

> 注：这是估算，实际看 token 消耗。ARTEX 有 Token 消耗面板（README:22 仪表盘），跑完能看真实用量对账。

---

## 下一步（等你装完 PostgreSQL）

你用官网安装包装好 PG、按上面第一件配好 `config.json` 的 dsn 后，ARTEX 就能起来：
```
set ARTEX_PG_DSN=postgres://artex:artex-local-drill-2026@127.0.0.1:5432/artex?sslmode=disable
set ARTEX_LLM_BASE_URL=http://127.0.0.1:7810/v1
set ANTHROPIC_API_KEY=
set OPENAI_API_KEY=
D:\refs\ARTEX-release\artex-0.3.29-windows-amd64\artex.exe -addr 127.0.0.1:8787 -proxy 
```
（或用刚编译的 `/tmp/artex-build-test.exe`。`config.json` 已含 dsn，环境变量那行可省。）

**当前仍未做**（如实交代，没假装）：PG 未装 → ARTEX 主体没启动 → 全自动演练和 5 个防守掺沙子的靶场验证还没跑。这两个等你确认 PG 装好后接着干，全部落 Windows 端、追加更新三份报告。
