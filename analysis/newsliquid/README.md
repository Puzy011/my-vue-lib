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
| `EVENT_SCHEMA.json` | 事件 JSON Schema（字段/阈值/去重/冷却） |
| `scan_events.py` | MVP 扫描：OI_SPIKE + OI_CONCENTRATION |
| `watch_pool/` | 观察池落盘（gitignore 大文件可保留样例） |

## 运行

```bash
python3 analysis/newsliquid/scan_events.py --once
python3 analysis/newsliquid/scan_events.py --once --out analysis/newsliquid/watch_pool/latest.json
```

## 执行层否决（推送后仍要过）

- 结构确认（禁止 RANGE 当单边）
- 短线 OI 背离一票否决
- tipH / tipL 不追
- 费率拥挤、24h 已翻倍 → 降级「观察/止盈」，禁止追开
