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

## 合约固定分析框架（强制）

用户问 `xxxusdt现价做多还是做空` 时，按 `AGENTS.md` + `analysis/beat_framework/RULES.md` 执行。

```bash
python3 analysis/beat_framework/analyze.py BEATUSDT
python3 analysis/newsliquid/scan_events.py --once
```

| 路径 | 作用 |
|------|------|
| `analysis/beat_framework/` | 8 步规则、报告模板、拉数引擎 |
| `analysis/newsliquid/` | 庄币启动雷达（观察池，禁止自动跟单） |
| `src/newsliquid/schemas/` | 前端/校验用事件 JSON Schema |
| `AGENTS.md` | Agent 强制执行入口 |

## NewsLiquid event schema

Watchlist-only market events (no auto-open):

- `src/newsliquid/schemas/event.schema.json`
- `src/newsliquid/schemas/event.examples.json`
- `tests/unit/newsliquidEventSchema.spec.js`

Event types: `OI_SPIKE` · `OI_CONCENTRATION` · `WHALE_PNL_START`

Rules baked in: structure confirmation required; short-term OI divergence / RANGE veto; crowded funding or 24h double → degrade to observe/take-profit.

```bash
npm run validate:schema
```
