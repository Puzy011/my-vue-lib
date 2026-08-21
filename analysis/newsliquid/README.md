# newsliquid — 庄币/异动启动雷达（观察池，禁止自动跟单）

## 定位

三维适合做 **启动雷达**；进场仍要结构+位置，否则专抓庄币会变成专给庄接盘。

事件 **只推观察池** → 是否开仓仍过 `beat_framework` 结构闸门 / 闸门F / tipH·tipL。

## MVP 落地顺序

1. ✅ `OI_SPIKE`：短窗 OI 增速过阈 + 增仓象限（立刻能扫 TUT/BMT 类）
2. ✅ `OI_CONCENTRATION`：Gate `top_*_size` / 总 OI 集中度代理
3. ⏳ `WHALE_PNL_START`：无付费聪明钱源前 **禁止假装有「主力已启动」**
4. ✅ 事件只进观察池；开仓另走结构闸门

## 文件

| 文件 | 作用 |
|------|------|
| `EVENT_SCHEMA.json` | 雷达落盘 Schema（snake_case：字段/阈值/去重/冷却；`pool` 固定 `observe`） |
| `../../src/newsliquid/schemas/event.schema.json` | 契约/UI Schema（camelCase + `executionGate`；`watchlistOnly: true`） |
| `scan_events.py` | MVP 扫描：OI_SPIKE + OI_CONCENTRATION |
| `scan_ambush.py` | 拉升/大跌埋伏筛选（位置闸门，禁止 tipH/tipL） |
| `watch_pool/` | 观察池落盘（gitignore 大文件可保留样例） |

两套 Schema 事件类型对齐：`OI_SPIKE` / `OI_CONCENTRATION` / `WHALE_PNL_START`。  
雷达产出进观察池；是否开仓仍走 `beat_framework` 结构闸门，**禁止自动跟单**。

## 运行

```bash
# 常规观察池扫描
python3 analysis/newsliquid/scan_events.py --once
python3 analysis/newsliquid/scan_events.py --once --out analysis/newsliquid/watch_pool/latest.json

# 启动期强庄雷达：OI 加速优先选窗 + 优先重扫
python3 analysis/newsliquid/scan_events.py --startup
python3 analysis/newsliquid/scan_events.py --startup --ignore-cooldown  # 强制全量重扫

# 拉升/大跌埋伏（中位、未贴高贴低；仍须过结构闸门）
python3 analysis/newsliquid/scan_ambush.py
```

### 启动期强庄 + OI 加速优先重扫

`--startup` 模式会：

1. **捕捉正在启动的强庄币**：`long_build` + 24h 涨幅 3%–60% + 非 tipH/未翻倍
2. **OI 加速选窗**：多时间窗同时过阈时，选 `oi_accel_5m` 最高的窗口（而非固定 5m 优先）
3. **优先重扫**：`oi_accel_5m ≥ 1.5` 的标的写入 `watch_pool/priority_rescan.json`，下次扫描优先纳入（即使不在涨幅榜前 40）
4. **动态冷却**：加速越高冷却越短（180s–900s），便于跟踪加速段

输出：`watch_pool/startup_latest.json`（含 `startup_long_watch`、`priority_rescan`）

## 执行层否决（推送后仍要过）

- 结构确认（禁止 RANGE 当单边）
- 短线 OI 背离一票否决
- tipH / tipL 不追
- 费率拥挤、24h 已翻倍 → 降级「观察/止盈」，禁止追开
