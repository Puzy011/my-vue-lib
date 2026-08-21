# BEATUSDT Beat固定框架报告
- 时间：2026-08-11 04:44:41 UTC
- 数据源：{'Gate': 'OK', 'OKX': 'OK', 'MEXC': 'OK', 'Bybit': 'N/A:HTTPError: HTTP Error 403: Forbidden', 'Binance': 'N/A:HTTPError: HTTP Error 451: '}

## 统一结论
•结论：观望
•依据：
  - 价格：主源Gate 1.4002 | 24h -46.96% | 高2.7771 低1.2191 | 位置11.6%
  - OI：OI强度：普通 ＋ 空增仓(已回落) ＋ 5m=-0.123 15m=-1.326 1h=-4.385 4h=31.545 | 减仓/去杠杆或短线OI回落，大变动不作极强 | 象限24h=Q2_跌价增仓 1h=Q3_涨价减仓 4h=Q1_涨价增仓
  - 结构：单边偏空 | 突破上=False 跌破=False
  - 周期：5m:中性/RSI=54.2/纠缠/阳 / 15m:偏空/RSI=53.9/空头排列/阳 / 1h:偏空/RSI=26.7/空头排列/阳 / 4h:偏空/RSI=30.6/空头排列/阳
  - 费率：开空未满足：需结构DOWN/跌破且OI仍空增仓（短线减仓不追）
•执行单：观望（不下手）
•失效条件：现价不追；若反抽至1.436附近且OI再增(Q2)可评估做空；失效=收盘站上该反抽高点

## 1 交易行情·现价
|交易所|现价|24h高|24h低|涨跌%|位置%|费率%|状态|
|---|---:|---:|---:|---:|---:|---:|---|
|Gate|1.4002|2.7771|1.2191|-46.96|11.6|0.01|OK|
|OKX|1.4002|2.7717|1.2144|-46.95|11.9|0.0259|OK|
|MEXC|1.402|2.776|1.221|-34.24|11.6|0.005|OK|
|Bybit|N/A|N/A|N/A|N/A|N/A|N/A|HTTPError: HTTP Error 403: Forbidden|
|Binance|N/A|N/A|N/A|N/A|N/A|N/A|HTTPError: HTTP Error 451: |

## 2 OI四象限
|周期|ΔOI%|象限|
|---|---:|---|
|5m|-0.123|Q3_涨价减仓|
|15m|-1.326|Q3_涨价减仓|
|1h|-4.385|Q3_涨价减仓|
|4h|31.545|Q1_涨价增仓|

## 3 结构
{"regime": "单边偏空", "is_range": false, "swing_high_1h": 1.9241, "swing_low_1h": 1.2191, "break_up": false, "break_down": false, "pos_pct": 11.62387676508343, "oi_grade": {"level": "普通", "direction": "空增仓(已回落)", "buildup": false, "deleveraging": true, "label": "OI强度：普通 ＋ 空增仓(已回落) ＋ 5m=-0.123 15m=-1.326 1h=-4.385 4h=31.545", "note": "减仓/去杠杆或短线OI回落，大变动不作极强", "hint": ""}}

## 4 周期 RSI/均线/阴阳
|周期|RSI|均线|阴阳|偏向|
|---|---:|---|---|---|
|5m|54.2|纠缠|阳|中性|
|15m|53.9|空头排列|阳|偏空|
|1h|26.7|空头排列|阳|偏空|
|4h|30.6|空头排列|阳|偏空|

## 5 资金费率 / 闸门F
{"pass": false, "note": "开空未满足：需结构DOWN/跌破且OI仍空增仓（短线减仓不追）", "funding_pct": 0.01}

## 6 事件 / 舆情 / 链上 / 大额转账
- CryptoPanic：N/A (HTTPError: HTTP Error 403: Forbidden)
- 舆情/社交：CoinGecko trending含BEAT=False
- 链上：N/A（当前环境无稳定链上接口）
- 大额转账：N/A（当前环境无大额转账接口）
- Fear&Greed：{'value': '29', 'class': 'Fear'}

## 7 市场环境
{"BTC": {"venue": "Gate", "last": 64071.1, "chg24": -1.4, "funding_pct": 0.0046, "is_range": true, "error": null, "oi_1h": -0.08115919874300825}, "ETH": {"venue": "Gate", "last": 1876.98, "chg24": -2.03, "funding_pct": -0.0060999999999999995, "is_range": false, "error": null, "oi_1h": -0.8014212432512102}}


```json
{
  "symbol": "BEATUSDT",
  "ts_utc": "2026-08-11 04:44:41 UTC",
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
      "last": 1.4002,
      "high": 2.7771,
      "low": 1.2191,
      "chg24": -46.96,
      "funding": 0.0001,
      "oi_usd": 3220854.52,
      "error": null
    },
    "OKX": {
      "venue": "OKX",
      "last": 1.4002,
      "high": 2.7717,
      "low": 1.2144,
      "chg24": -46.952074256487975,
      "funding": 0.0002593887572712,
      "oi_usd": 9131286.7846,
      "error": null
    },
    "MEXC": {
      "venue": "MEXC",
      "last": 1.402,
      "high": 2.776,
      "low": 1.221,
      "chg24": -34.239999999999995,
      "funding": 5e-05,
      "oi_usd": 7058263.85,
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
    "5m": -0.123,
    "15m": -1.326,
    "1h": -4.385,
    "4h": 31.545,
    "24h_proxy": 31.545
  },
  "oi_quadrants": {
    "5m": "Q3_涨价减仓",
    "15m": "Q3_涨价减仓",
    "1h": "Q3_涨价减仓",
    "4h": "Q1_涨价增仓",
    "24h": "Q2_跌价增仓"
  },
  "structure": {
    "regime": "单边偏空",
    "is_range": false,
    "swing_high_1h": 1.9241,
    "swing_low_1h": 1.2191,
    "break_up": false,
    "break_down": false,
    "pos_pct": 11.62387676508343,
    "oi_grade": {
      "level": "普通",
      "direction": "空增仓(已回落)",
      "buildup": false,
      "deleveraging": true,
      "label": "OI强度：普通 ＋ 空增仓(已回落) ＋ 5m=-0.123 15m=-1.326 1h=-4.385 4h=31.545",
      "note": "减仓/去杠杆或短线OI回落，大变动不作极强",
      "hint": ""
    }
  },
  "tf": {
    "5m": {
      "tf": "5m",
      "rsi": 54.165021713383304,
      "ema20": 1.3548918834540489,
      "ema50": 1.3917237583696556,
      "above_ema20": true,
      "ma_rel": "纠缠",
      "candle": "阳",
      "px_chg": 1.8634444606201894,
      "swing_high": 1.436,
      "swing_low": 1.3038,
      "bias": "中性"
    },
    "15m": {
      "tf": "15m",
      "rsi": 53.89095992544267,
      "ema20": 1.4089933527746894,
      "ema50": 1.622056166263062,
      "above_ema20": false,
      "ma_rel": "空头排列",
      "candle": "阳",
      "px_chg": 4.401671142942409,
      "swing_high": 1.436,
      "swing_low": 1.2191,
      "bias": "偏空"
    },
    "1h": {
      "tf": "1h",
      "rsi": 26.727526309116257,
      "ema20": 1.836061936554641,
      "ema50": 2.2921283719481815,
      "above_ema20": false,
      "ma_rel": "空头排列",
      "candle": "阳",
      "px_chg": -26.53928927615349,
      "swing_high": 1.9241,
      "swing_low": 1.2191,
      "bias": "偏空"
    },
    "4h": {
      "tf": "4h",
      "rsi": 30.630295625381805,
      "ema20": 2.3269514906110627,
      "ema50": 2.628893864339643,
      "above_ema20": false,
      "ma_rel": "空头排列",
      "candle": "阳",
      "px_chg": -56.87476888943671,
      "swing_high": 3.9755,
      "swing_low": 1.2191,
      "bias": "偏空"
    }
  },
  "gate_f": {
    "pass": false,
    "note": "开空未满足：需结构DOWN/跌破且OI仍空增仓（短线减仓不追）",
    "funding_pct": 0.01
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
          "DOS",
          "PENGU",
          "STONKBROKER",
          "CASHCAT",
          "PEPE",
          "PUMP",
          "LINK",
          "LIT",
          "BLUAI",
          "TAO"
        ]
      }
    ]
  },
  "market": {
    "BTC": {
      "venue": "Gate",
      "last": 64071.1,
      "chg24": -1.4,
      "funding_pct": 0.0046,
      "is_range": true,
      "error": null,
      "oi_1h": -0.08115919874300825
    },
    "ETH": {
      "venue": "Gate",
      "last": 1876.98,
      "chg24": -2.03,
      "funding_pct": -0.0060999999999999995,
      "is_range": false,
      "error": null,
      "oi_1h": -0.8014212432512102
    }
  },
  "结论": "观望",
  "依据": {
    "价格": "主源Gate 1.4002 | 24h -46.96% | 高2.7771 低1.2191 | 位置11.6%",
    "OI": "OI强度：普通 ＋ 空增仓(已回落) ＋ 5m=-0.123 15m=-1.326 1h=-4.385 4h=31.545 | 减仓/去杠杆或短线OI回落，大变动不作极强 | 象限24h=Q2_跌价增仓 1h=Q3_涨价减仓 4h=Q1_涨价增仓",
    "结构": "单边偏空 | 突破上=False 跌破=False",
    "周期": "5m:中性/RSI=54.2/纠缠/阳 / 15m:偏空/RSI=53.9/空头排列/阳 / 1h:偏空/RSI=26.7/空头排列/阳 / 4h:偏空/RSI=30.6/空头排列/阳",
    "费率": "开空未满足：需结构DOWN/跌破且OI仍空增仓（短线减仓不追）"
  },
  "执行单": {
    "side": "观望",
    "entry": null,
    "stop": null,
    "tp1": null,
    "tp2": null
  },
  "失效条件": "现价不追；若反抽至1.436附近且OI再增(Q2)可评估做空；失效=收盘站上该反抽高点"
}
```
