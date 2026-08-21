# my-vue-lib

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Run your unit tests
```
npm run test:unit
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

---

## 合约分析（强制框架）

用户发送 `xxxusdt现价做多还是做空` 时，**必须**按固定 8 步 + 统一输出；Agent 入口见 `AGENTS.md`。

| 路径 | 作用 |
|------|------|
| `analysis/beat_framework/RULES.md` | 硬规则：OI 筛选、闸门 F、RANGE 禁单边、推荐闸门、OI 强度 |
| `analysis/beat_framework/REPORT_TEMPLATE.md` | 固化报告：行情/链上/舆情/大额转账/衍生品/CryptoPanic/市场环境 |
| `analysis/beat_framework/analyze.py` | 拉 Gate/OKX/MEXC(+Bybit/Binance) 实时数据并输出可执行结论 |
| `analysis/newsliquid/` | 庄币启动雷达（`OI_SPIKE` / `OI_CONCENTRATION` / `WHALE_PNL_START`）→ **仅观察池** |
| `src/newsliquid/schemas/` | UI/契约侧 camelCase 事件 Schema（`watchlistOnly: true`） |

### 推荐硬闸门（摘要）

1. 短线空增仓 / EMA 空头 → **默认观望，禁止现价多**
2. 开多必须：**结构 UP 或突破确认 + OI 仍多增仓**
3. 「OI 强/极强」只筛选，不是开仓许可；减仓禁止标极强；未过闸门写 **极强但观望**
4. tipH/tipL 不追；费率拥挤 / 24h 翻倍 → 观察/止盈，禁止追开

### 统一输出

```
•结论：做多/做空/观望/极强但观望
•依据：价格；OI强度：x＋方向＋5m/15m/1h/4h；结构；周期；费率
•执行单：入场 / 止损 / 止盈
•失效条件：...
```

### 命令

```bash
python3 analysis/beat_framework/analyze.py BEATUSDT
python3 analysis/newsliquid/scan_events.py --once
python3 analysis/newsliquid/scan_events.py --startup
npm run validate:schema
npm run test:unit
```

`main` **不承载**实时行情；数据以当时能拉到的交易所为准，拉不到标 `N/A`。

## NewsLiquid event schema

- `src/newsliquid/schemas/event.schema.json` — 完整上下文 + `executionGate`（契约/UI）
- `analysis/newsliquid/EVENT_SCHEMA.json` — 雷达扫描落盘（snake_case，`pool: "observe"`）
- 两套枚举对齐：`OI_SPIKE` / `OI_CONCENTRATION` / `WHALE_PNL_START`；无付费 PnL 源前 `WHALE_PNL_START` 必须 `blocked`

Quick validation:

```
npm run validate:schema
```
