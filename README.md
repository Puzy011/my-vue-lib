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

## NewsLiquid event schema

This repository now includes a minimal event schema for watchlist-only market events:

- `src/newsliquid/schemas/event.schema.json`
- `src/newsliquid/schemas/event.examples.json`
- `tests/unit/newsliquidEventSchema.spec.js`

Current supported event types:

- `OI_SPIKE`
- `OI_CONCENTRATION`
- `WHALE_PNL_START`

Design rules baked into the schema:

- Events are watchlist-only and do not auto-open positions.
- Structure confirmation is required before execution.
- Short-term OI divergence and range regime can veto execution.
- Crowded funding and daily doubling should degrade an event to observation.

Quick validation without installing frontend dependencies:

```
npm run validate:schema
```

## 合约分析框架（固定 8 步）

用户发 `xxxusdt现价做多还是做空` 时，运行：

```bash
python3 scripts/analyze_contract.py BTCUSDT
```

- 规范：`docs/trading/ANALYSIS_FRAMEWORK.md`
- 硬规则：`analysis/beat_framework/RULES.md`
- 报告模板：`analysis/beat_framework/REPORT_TEMPLATE.md`
- 庄币/OI 雷达（观察池）：`python3 analysis/newsliquid/scan_events.py --startup`

事件 JSON 契约与 `main` 一致：`src/newsliquid/schemas/event.schema.json`
