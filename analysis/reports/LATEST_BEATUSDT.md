# BEATUSDT Beat固定框架报告
- 时间：2026-08-20 18:45:38 UTC
- 数据源：{'Gate': 'OK', 'OKX': 'OK', 'MEXC': 'OK', 'Bybit': 'N/A:HTTPError: HTTP Error 403: Forbidden', 'Binance': 'N/A:HTTPError: HTTP Error 451: '}

## 统一结论
•结论：观望
•依据：
  - 价格：主源Gate 0.148 | 24h -7.67% | 高0.174 低0.1184 | 位置53.2%
  - OI：OI强度：普通 ＋ 空增仓(短线微增/高周期减仓) ＋ 5m=0.613 15m=0.321 1h=-1.727 4h=-9.714 | 减仓/去杠杆，大变动不作极强/强 | 象限24h=Q4_跌价减仓 1h=Q4_跌价减仓 4h=Q3_涨价减仓
  - 结构：震荡RANGE | 突破上=False 跌破=False
  - 周期：5m:中性/RSI=38.6/多头排列/阴 / 15m:偏多/RSI=63.1/多头排列/阴 / 1h:中性/RSI=48.2/纠缠/阴 / 4h:偏空/RSI=17.0/空头排列/阳
  - 费率：RANGE不当单边
•执行单：观望（不下手）
•失效条件：需结构UP/DOWN确认 + OI仍同向增仓 + 过闸门F；tipH/tipL不追

## 1 交易行情·现价
|交易所|现价|24h高|24h低|涨跌%|位置%|费率%|状态|
|---|---:|---:|---:|---:|---:|---:|---|
|Gate|0.148|0.174|0.1184|-7.67|53.2|0.01|OK|
|OKX|0.1479|0.1745|0.1192|-8.02|51.9|0.0184|OK|
|MEXC|0.148|0.174|0.1183|13.4|53.3|0.0175|OK|
|Bybit|N/A|N/A|N/A|N/A|N/A|N/A|HTTPError: HTTP Error 403: Forbidden|
|Binance|N/A|N/A|N/A|N/A|N/A|N/A|HTTPError: HTTP Error 451: |

## 2 OI四象限
|周期|ΔOI%|象限|
|---|---:|---|
|5m|0.613|Q2_跌价增仓|
|15m|0.321|Q2_跌价增仓|
|1h|-1.727|Q4_跌价减仓|
|4h|-9.714|Q3_涨价减仓|

## 3 结构
{"regime": "震荡RANGE", "is_range": true, "swing_high_1h": 0.1579, "swing_low_1h": 0.1184, "break_up": false, "break_down": false, "pos_pct": 53.237410071942435, "oi_grade": {"level": "普通", "direction": "空增仓(短线微增/高周期减仓)", "buildup": false, "deleveraging": true, "label": "OI强度：普通 ＋ 空增仓(短线微增/高周期减仓) ＋ 5m=0.613 15m=0.321 1h=-1.727 4h=-9.714", "note": "减仓/去杠杆，大变动不作极强/强", "hint": ""}}

## 4 周期 RSI/均线/阴阳
|周期|RSI|均线|阴阳|偏向|
|---|---:|---|---|---|
|5m|38.6|多头排列|阴|中性|
|15m|63.1|多头排列|阴|偏多|
|1h|48.2|纠缠|阴|中性|
|4h|17.0|空头排列|阳|偏空|

## 5 资金费率 / 闸门F
{"pass": false, "funding_pct": 0.01, "note": "RANGE不当单边"}

## 6 事件 / 舆情 / 链上 / 大额转账
- CryptoPanic：N/A (HTTPError: HTTP Error 403: Forbidden)
- 舆情/社交：CoinGecko trending含BEAT=False
- 链上：N/A（当前环境无稳定链上接口）
- 大额转账：N/A（当前环境无大额转账接口）
- Fear&Greed：{'value': '62', 'class': 'Greed'}

## 7 市场环境
{"BTC": {"venue": "Gate", "last": 72464.0, "chg24": 5.93, "funding_pct": -0.0015999999999999999, "is_range": false, "error": null, "oi_1h": -1.4579131005057921}, "ETH": {"venue": "Gate", "last": 2314.05, "chg24": 10.71, "funding_pct": 0.0081, "is_range": false, "error": null, "oi_1h": -2.8383484743782827}}


```json
{
  "symbol": "BEATUSDT",
  "ts_utc": "2026-08-20 18:45:38 UTC",
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
      "last": 0.148,
      "high": 0.174,
      "low": 0.1184,
      "chg24": -7.67,
      "funding": 0.0001,
      "oi_usd": 4616333.37,
      "error": null
    },
    "OKX": {
      "venue": "OKX",
      "last": 0.1479,
      "high": 0.1745,
      "low": 0.1192,
      "chg24": -8.022388059701491,
      "funding": 0.0001841485512246,
      "oi_usd": 5632409.4723000005,
      "error": null
    },
    "MEXC": {
      "venue": "MEXC",
      "last": 0.148,
      "high": 0.174,
      "low": 0.1183,
      "chg24": 13.4,
      "funding": 0.000175,
      "oi_usd": 8100153.072,
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
    "5m": 0.613,
    "15m": 0.321,
    "1h": -1.727,
    "4h": -9.714,
    "24h_proxy": -9.714
  },
  "oi_quadrants": {
    "5m": "Q2_跌价增仓",
    "15m": "Q2_跌价增仓",
    "1h": "Q4_跌价减仓",
    "4h": "Q3_涨价减仓",
    "24h": "Q4_跌价减仓"
  },
  "structure": {
    "regime": "震荡RANGE",
    "is_range": true,
    "swing_high_1h": 0.1579,
    "swing_low_1h": 0.1184,
    "break_up": false,
    "break_down": false,
    "pos_pct": 53.237410071942435,
    "oi_grade": {
      "level": "普通",
      "direction": "空增仓(短线微增/高周期减仓)",
      "buildup": false,
      "deleveraging": true,
      "label": "OI强度：普通 ＋ 空增仓(短线微增/高周期减仓) ＋ 5m=0.613 15m=0.321 1h=-1.727 4h=-9.714",
      "note": "减仓/去杠杆，大变动不作极强/强",
      "hint": ""
    }
  },
  "tf": {
    "5m": {
      "tf": "5m",
      "rsi": 38.5542168674699,
      "ema20": 0.14595981935618627,
      "ema50": 0.13987012867051357,
      "above_ema20": true,
      "ma_rel": "多头排列",
      "candle": "阴",
      "px_chg": -0.6729475100942128,
      "swing_high": 0.1553,
      "swing_low": 0.1459,
      "bias": "中性"
    },
    "15m": {
      "tf": "15m",
      "rsi": 63.13993174061432,
      "ema20": 0.13993752658137995,
      "ema50": 0.13938198768110435,
      "above_ema20": true,
      "ma_rel": "多头排列",
      "candle": "阴",
      "px_chg": 13.353798925556415,
      "swing_high": 0.1579,
      "swing_low": 0.1184,
      "bias": "偏多"
    },
    "1h": {
      "tf": "1h",
      "rsi": 48.17001180637544,
      "ema20": 0.14578467358293115,
      "ema50": 0.1745347583443623,
      "above_ema20": true,
      "ma_rel": "纠缠",
      "candle": "阴",
      "px_chg": 3.4313725490195957,
      "swing_high": 0.1579,
      "swing_low": 0.1184,
      "bias": "中性"
    },
    "4h": {
      "tf": "4h",
      "rsi": 17.037552155771905,
      "ema20": 0.2254635187570721,
      "ema50": 0.5480711867235848,
      "above_ema20": false,
      "ma_rel": "空头排列",
      "candle": "阳",
      "px_chg": -35.50218340611354,
      "swing_high": 0.2459,
      "swing_low": 0.1184,
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
      "value": "62",
      "class": "Greed"
    },
    "onchain": "N/A（当前环境无稳定链上接口）",
    "whales": "N/A（当前环境无大额转账接口）",
    "social": "CoinGecko trending含BEAT=False",
    "news": [
      {
        "source": "coingecko_trending",
        "symbols": [
          "ERG",
          "BULLBALLS",
          "ALIGN",
          "PIPEDOG",
          "HYPE",
          "BTC",
          "SOL",
          "PUMP",
          "MON",
          "ENA"
        ]
      }
    ]
  },
  "market": {
    "BTC": {
      "venue": "Gate",
      "last": 72464.0,
      "chg24": 5.93,
      "funding_pct": -0.0015999999999999999,
      "is_range": false,
      "error": null,
      "oi_1h": -1.4579131005057921
    },
    "ETH": {
      "venue": "Gate",
      "last": 2314.05,
      "chg24": 10.71,
      "funding_pct": 0.0081,
      "is_range": false,
      "error": null,
      "oi_1h": -2.8383484743782827
    }
  },
  "结论": "观望",
  "依据": {
    "价格": "主源Gate 0.148 | 24h -7.67% | 高0.174 低0.1184 | 位置53.2%",
    "OI": "OI强度：普通 ＋ 空增仓(短线微增/高周期减仓) ＋ 5m=0.613 15m=0.321 1h=-1.727 4h=-9.714 | 减仓/去杠杆，大变动不作极强/强 | 象限24h=Q4_跌价减仓 1h=Q4_跌价减仓 4h=Q3_涨价减仓",
    "结构": "震荡RANGE | 突破上=False 跌破=False",
    "周期": "5m:中性/RSI=38.6/多头排列/阴 / 15m:偏多/RSI=63.1/多头排列/阴 / 1h:中性/RSI=48.2/纠缠/阴 / 4h:偏空/RSI=17.0/空头排列/阳",
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
