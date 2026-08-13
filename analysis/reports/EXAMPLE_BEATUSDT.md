# BEATUSDT Beat固定框架报告
- 时间：2026-08-13 17:40:58 UTC
- 数据源：{'Gate': 'OK', 'OKX': 'OK', 'MEXC': 'OK', 'Bybit': 'N/A:HTTPError: HTTP Error 403: Forbidden', 'Binance': 'N/A:HTTPError: HTTP Error 451: '}

## 统一结论
•结论：观望
•依据：
  - 价格：主源Gate 0.9398 | 24h -10.33% | 高1.2265 低0.8232 | 位置28.9%
  - OI：OI强度：普通 ＋ 跌价减仓 ＋ 5m=-0.449 15m=0.143 1h=-1.204 4h=-6.108 | 减仓/去杠杆或短线OI回落，大变动不作极强 | 象限24h=Q4_跌价减仓 1h=Q4_跌价减仓 4h=Q3_涨价减仓
  - 结构：震荡RANGE | 突破上=False 跌破=False
  - 周期：5m:偏多/RSI=47.3/多头排列/阴 / 15m:中性/RSI=62.1/纠缠/阴 / 1h:偏空/RSI=50.2/空头排列/阴 / 4h:偏空/RSI=51.4/空头排列/阳
  - 费率：RANGE不当单边
•执行单：观望（不下手）
•失效条件：需结构UP/DOWN确认 + OI仍同向增仓 + 过闸门F；tipH/tipL不追

## 1 交易行情·现价
|交易所|现价|24h高|24h低|涨跌%|位置%|费率%|状态|
|---|---:|---:|---:|---:|---:|---:|---|
|Gate|0.9398|1.2265|0.8232|-10.33|28.9|0.01|OK|
|OKX|0.9402|1.2253|0.8203|-10.29|29.6|0.005|OK|
|MEXC|0.942|1.223|0.818|4.78|30.6|0.005|OK|
|Bybit|N/A|N/A|N/A|N/A|N/A|N/A|HTTPError: HTTP Error 403: Forbidden|
|Binance|N/A|N/A|N/A|N/A|N/A|N/A|HTTPError: HTTP Error 451: |

## 2 OI四象限
|周期|ΔOI%|象限|
|---|---:|---|
|5m|-0.449|Q4_跌价减仓|
|15m|0.143|Q2_跌价增仓|
|1h|-1.204|Q4_跌价减仓|
|4h|-6.108|Q3_涨价减仓|

## 3 结构
{"regime": "震荡RANGE", "is_range": true, "swing_high_1h": 1.0275, "swing_low_1h": 0.8232, "break_up": false, "break_down": false, "pos_pct": 28.911480287627068, "oi_grade": {"level": "普通", "direction": "跌价减仓", "buildup": false, "deleveraging": true, "label": "OI强度：普通 ＋ 跌价减仓 ＋ 5m=-0.449 15m=0.143 1h=-1.204 4h=-6.108", "note": "减仓/去杠杆或短线OI回落，大变动不作极强", "hint": ""}}

## 4 周期 RSI/均线/阴阳
|周期|RSI|均线|阴阳|偏向|
|---|---:|---|---|---|
|5m|47.3|多头排列|阴|偏多|
|15m|62.1|纠缠|阴|中性|
|1h|50.2|空头排列|阴|偏空|
|4h|51.4|空头排列|阳|偏空|

## 5 资金费率 / 闸门F
{"pass": false, "funding_pct": 0.01, "note": "RANGE不当单边"}

## 6 事件 / 舆情 / 链上 / 大额转账
- CryptoPanic：N/A (HTTPError: HTTP Error 403: Forbidden)
- 舆情/社交：CoinGecko trending含BEAT=False
- 链上：N/A（当前环境无稳定链上接口）
- 大额转账：N/A（当前环境无大额转账接口）
- Fear&Greed：{'value': '29', 'class': 'Fear'}

## 7 市场环境
{"BTC": {"venue": "Gate", "last": 63165.8, "chg24": -0.49, "funding_pct": 0.009000000000000001, "is_range": true, "error": null, "oi_1h": -3.9100171842837317}, "ETH": {"venue": "Gate", "last": 1877.75, "chg24": -0.58, "funding_pct": 0.01, "is_range": true, "error": null, "oi_1h": -1.1899678866189478}}


```json
{
  "symbol": "BEATUSDT",
  "ts_utc": "2026-08-13 17:40:58 UTC",
  "sources": {
    "Gate": "OK",
    "OKX": "OK",
    "MEXC": "OK",
    "Bybit": "N/A:HTTPError: HTTP Error 403: Forbidden",
    "Binance": "N/A:HTTPError: HTTP Error 451: "
  },
  "quotes": {
    "Gate": {
      "venue": "Gate",
      "last": 0.9398,
      "high": 1.2265,
      "low": 0.8232,
      "chg24": -10.33,
      "funding": 0.0001,
      "oi_usd": 3229730.106,
      "error": null
    },
    "OKX": {
      "venue": "OKX",
      "last": 0.9402,
      "high": 1.2253,
      "low": 0.8203,
      "chg24": -10.294819196641535,
      "funding": 5e-05,
      "oi_usd": 7556991.372000004,
      "error": null
    },
    "MEXC": {
      "venue": "MEXC",
      "last": 0.942,
      "high": 1.223,
      "low": 0.818,
      "chg24": 4.78,
      "funding": 5e-05,
      "oi_usd": 8229878.142,
      "error": null
    },
    "Bybit": {
      "venue": "Bybit",
      "last": null,
      "high": null,
      "low": null,
      "chg24": null,
      "funding": null,
      "oi_usd": null,
      "error": "HTTPError: HTTP Error 403: Forbidden"
    },
    "Binance": {
      "venue": "Binance",
      "last": null,
      "high": null,
      "low": null,
      "chg24": null,
      "funding": null,
      "oi_usd": null,
      "error": "HTTPError: HTTP Error 451: "
    }
  },
  "oi_changes": {
    "5m": -0.449,
    "15m": 0.143,
    "1h": -1.204,
    "4h": -6.108,
    "24h_proxy": -6.108
  },
  "oi_quadrants": {
    "5m": "Q4_跌价减仓",
    "15m": "Q2_跌价增仓",
    "1h": "Q4_跌价减仓",
    "4h": "Q3_涨价减仓",
    "24h": "Q4_跌价减仓"
  },
  "structure": {
    "regime": "震荡RANGE",
    "is_range": true,
    "swing_high_1h": 1.0275,
    "swing_low_1h": 0.8232,
    "break_up": false,
    "break_down": false,
    "pos_pct": 28.911480287627068,
    "oi_grade": {
      "level": "普通",
      "direction": "跌价减仓",
      "buildup": false,
      "deleveraging": true,
      "label": "OI强度：普通 ＋ 跌价减仓 ＋ 5m=-0.449 15m=0.143 1h=-1.204 4h=-6.108",
      "note": "减仓/去杠杆或短线OI回落，大变动不作极强",
      "hint": ""
    }
  },
  "tf": {
    "5m": {
      "tf": "5m",
      "rsi": 47.33824733824732,
      "ema20": 0.9396210621547026,
      "ema50": 0.9251152365777291,
      "above_ema20": true,
      "ma_rel": "多头排列",
      "candle": "阴",
      "px_chg": 1.1082418764794433,
      "swing_high": 0.9957,
      "swing_low": 0.9294,
      "bias": "偏多"
    },
    "15m": {
      "tf": "15m",
      "rsi": 62.139917695473265,
      "ema20": 0.9246467067836693,
      "ema50": 0.942637801178974,
      "above_ema20": true,
      "ma_rel": "纠缠",
      "candle": "阴",
      "px_chg": 4.342032204330937,
      "swing_high": 0.9957,
      "swing_low": 0.8232,
      "bias": "中性"
    },
    "1h": {
      "tf": "1h",
      "rsi": 50.21263669501822,
      "ema20": 0.9622101664808018,
      "ema50": 1.0995428200708846,
      "above_ema20": false,
      "ma_rel": "空头排列",
      "candle": "阴",
      "px_chg": -6.4888535031847105,
      "swing_high": 1.0275,
      "swing_low": 0.8232,
      "bias": "偏空"
    },
    "4h": {
      "tf": "4h",
      "rsi": 51.40532544378698,
      "ema20": 1.2962199203399045,
      "ema50": 1.9180268888049843,
      "above_ema20": false,
      "ma_rel": "空头排列",
      "candle": "阳",
      "px_chg": -5.272708942433713,
      "swing_high": 1.3977,
      "swing_low": 0.8232,
      "bias": "偏空"
    }
  },
  "gate_f": {
    "pass": false,
    "funding_pct": 0.01,
    "note": "RANGE不当单边"
  },
  "events": {
    "cryptopanic": "N/A (HTTPError: HTTP Error 403: Forbidden)",
    "fear_greed": {
      "value": "29",
      "class": "Fear"
    },
    "onchain": "N/A（当前环境无稳定链上接口）",
    "whales": "N/A（当前环境无大额转账接口）",
    "social": "CoinGecko trending含BEAT=False",
    "news": [
      {
        "source": "coingecko_trending",
        "symbols": [
          "ETHFI",
          "BTC",
          "PUMP",
          "SOL",
          "ETH",
          "APR",
          "DEUS",
          "CASHCAT",
          "XRP",
          "HYPE"
        ]
      }
    ]
  },
  "market": {
    "BTC": {
      "venue": "Gate",
      "last": 63165.8,
      "chg24": -0.49,
      "funding_pct": 0.009000000000000001,
      "is_range": true,
      "error": null,
      "oi_1h": -3.9100171842837317
    },
    "ETH": {
      "venue": "Gate",
      "last": 1877.75,
      "chg24": -0.58,
      "funding_pct": 0.01,
      "is_range": true,
      "error": null,
      "oi_1h": -1.1899678866189478
    }
  },
  "结论": "观望",
  "依据": {
    "价格": "主源Gate 0.9398 | 24h -10.33% | 高1.2265 低0.8232 | 位置28.9%",
    "OI": "OI强度：普通 ＋ 跌价减仓 ＋ 5m=-0.449 15m=0.143 1h=-1.204 4h=-6.108 | 减仓/去杠杆或短线OI回落，大变动不作极强 | 象限24h=Q4_跌价减仓 1h=Q4_跌价减仓 4h=Q3_涨价减仓",
    "结构": "震荡RANGE | 突破上=False 跌破=False",
    "周期": "5m:偏多/RSI=47.3/多头排列/阴 / 15m:中性/RSI=62.1/纠缠/阴 / 1h:偏空/RSI=50.2/空头排列/阴 / 4h:偏空/RSI=51.4/空头排列/阳",
    "费率": "RANGE不当单边"
  },
  "执行单": {
    "side": "观望",
    "entry": null,
    "stop": null,
    "tp1": null,
    "tp2": null
  },
  "失效条件": "需结构UP/DOWN确认 + OI仍同向增仓 + 过闸门F；tipH/tipL不追"
}
```
