# BEATUSDT Beat固定框架报告
- 时间：2026-08-11 04:34:52 UTC
- 数据源：{'Gate': 'OK', 'OKX': 'OK', 'MEXC': 'OK', 'Bybit': 'N/A:HTTPError: HTTP Error 403: Forbidden', 'Binance': 'N/A:HTTPError: HTTP Error 451: '}

## 统一结论
•结论：观望
•依据：
  - 价格：主源Gate 1.3739 | 24h -47.15% | 高2.7771 低1.2191 | 位置9.9%
  - OI：5m=-0.756 15m=-1.162 1h=-2.649 4h=41.614 | 象限24h=Q2_跌价增仓 1h=Q3_涨价减仓 4h=Q1_涨价增仓 | OI强筛选=Y
  - 结构：单边偏空 | 突破上=False 跌破=False
  - 周期：5m:中性/RSI=52.6/纠缠/阴 / 15m:偏空/RSI=50.9/空头排列/阴 / 1h:偏空/RSI=25.5/空头排列/阳 / 4h:偏空/RSI=30.2/空头排列/阳
  - 费率：短周期OI回落(15m/1h减仓)，垂直下跌后不追空；费率=0.0100%
•执行单：观望（不下手）
•失效条件：现价不追空；若反抽至1.4265附近且OI再增(Q2)可转做空；失效=收盘站上该反抽高点

## 1 交易行情·现价
|交易所|现价|24h高|24h低|涨跌%|位置%|费率%|状态|
|---|---:|---:|---:|---:|---:|---:|---|
|Gate|1.3739|2.7771|1.2191|-47.15|9.9|0.01|OK|
|OKX|1.3737|2.7717|1.2144|-47.22|10.2|0.0286|OK|
|MEXC|1.374|2.776|1.221|-35.55|9.8|0.005|OK|
|Bybit|N/A|N/A|N/A|N/A|N/A|N/A|HTTPError: HTTP Error 403: Forbidden|
|Binance|N/A|N/A|N/A|N/A|N/A|N/A|HTTPError: HTTP Error 451: |

## 2 OI四象限
|周期|ΔOI%|象限|
|---|---:|---|
|5m|-0.756|Q4_跌价减仓|
|15m|-1.162|Q4_跌价减仓|
|1h|-2.649|Q3_涨价减仓|
|4h|41.614|Q1_涨价增仓|

## 3 结构
{"regime": "单边偏空", "is_range": false, "swing_high_1h": 1.9241, "swing_low_1h": 1.2191, "break_up": false, "break_down": false, "pos_pct": 9.935815147625151}

## 4 周期 RSI/均线/阴阳
|周期|RSI|均线|阴阳|偏向|
|---|---:|---|---|---|
|5m|52.6|纠缠|阴|中性|
|15m|50.9|空头排列|阴|偏空|
|1h|25.5|空头排列|阳|偏空|
|4h|30.2|空头排列|阳|偏空|

## 5 资金费率 / 闸门F
{"pass": false, "note": "短周期OI回落(15m/1h减仓)，垂直下跌后不追空；费率=0.0100%", "funding_pct": 0.01}

## 6 事件 / 舆情 / 链上 / 大额转账
- CryptoPanic：N/A (HTTPError: HTTP Error 403: Forbidden)
- 舆情/社交：CoinGecko trending含BEAT=False
- 链上：N/A（当前环境无稳定链上接口）
- 大额转账：N/A（当前环境无大额转账接口）
- Fear&Greed：{'value': '29', 'class': 'Fear'}

## 7 市场环境
{"BTC": {"venue": "Gate", "last": 64068.7, "chg24": -1.44, "funding_pct": 0.004699999999999999, "is_range": true, "error": null, "oi_1h": -0.11276066236906024}, "ETH": {"venue": "Gate", "last": 1877.78, "chg24": -2.15, "funding_pct": -0.006200000000000001, "is_range": false, "error": null, "oi_1h": -0.40261330447380894}}


```json
{
  "symbol": "BEATUSDT",
  "ts_utc": "2026-08-11 04:34:52 UTC",
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
      "last": 1.3739,
      "high": 2.7771,
      "low": 1.2191,
      "chg24": -47.15,
      "funding": 0.0001,
      "oi_usd": 3229309.148,
      "error": null
    },
    "OKX": {
      "venue": "OKX",
      "last": 1.3737,
      "high": 2.7717,
      "low": 1.2144,
      "chg24": -47.21613832853026,
      "funding": 0.0002861345309773,
      "oi_usd": 9181360.1945,
      "error": null
    },
    "MEXC": {
      "venue": "MEXC",
      "last": 1.374,
      "high": 2.776,
      "low": 1.221,
      "chg24": -35.55,
      "funding": 5e-05,
      "oi_usd": 6877202.508,
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
    "5m": -0.756,
    "15m": -1.162,
    "1h": -2.649,
    "4h": 41.614,
    "24h_proxy": 41.614
  },
  "oi_quadrants": {
    "5m": "Q4_跌价减仓",
    "15m": "Q4_跌价减仓",
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
    "pos_pct": 9.935815147625151
  },
  "tf": {
    "5m": {
      "tf": "5m",
      "rsi": 52.629449838187675,
      "ema20": 1.3474462694494913,
      "ema50": 1.391531557313934,
      "above_ema20": true,
      "ma_rel": "纠缠",
      "candle": "阴",
      "px_chg": -0.32648915330480976,
      "swing_high": 1.4265,
      "swing_low": 1.3038,
      "bias": "中性"
    },
    "15m": {
      "tf": "15m",
      "rsi": 50.92373282804356,
      "ema20": 1.406555257536594,
      "ema50": 1.6210522446944344,
      "above_ema20": false,
      "ma_rel": "空头排列",
      "candle": "阴",
      "px_chg": 2.4917934944792552,
      "swing_high": 1.4265,
      "swing_low": 1.2191,
      "bias": "偏空"
    },
    "1h": {
      "tf": "1h",
      "rsi": 25.51395243926015,
      "ema20": 1.8336143175070219,
      "ema50": 2.291120528810927,
      "above_ema20": false,
      "ma_rel": "空头排列",
      "candle": "阳",
      "px_chg": -27.88829982678075,
      "swing_high": 1.9241,
      "swing_low": 1.2191,
      "bias": "偏空"
    },
    "4h": {
      "tf": "4h",
      "rsi": 30.153508771929822,
      "ema20": 2.3245038715634436,
      "ema50": 2.6278860212023885,
      "above_ema20": false,
      "ma_rel": "空头排列",
      "candle": "阳",
      "px_chg": -57.66670775298903,
      "swing_high": 3.9755,
      "swing_low": 1.2191,
      "bias": "偏空"
    }
  },
  "gate_f": {
    "pass": false,
    "note": "短周期OI回落(15m/1h减仓)，垂直下跌后不追空；费率=0.0100%",
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
          "LINK",
          "PEPE",
          "BLUAI",
          "PUMP",
          "BTC",
          "LIT",
          "CASHCAT"
        ]
      }
    ]
  },
  "market": {
    "BTC": {
      "venue": "Gate",
      "last": 64068.7,
      "chg24": -1.44,
      "funding_pct": 0.004699999999999999,
      "is_range": true,
      "error": null,
      "oi_1h": -0.11276066236906024
    },
    "ETH": {
      "venue": "Gate",
      "last": 1877.78,
      "chg24": -2.15,
      "funding_pct": -0.006200000000000001,
      "is_range": false,
      "error": null,
      "oi_1h": -0.40261330447380894
    }
  },
  "结论": "观望",
  "依据": {
    "价格": "主源Gate 1.3739 | 24h -47.15% | 高2.7771 低1.2191 | 位置9.9%",
    "OI": "5m=-0.756 15m=-1.162 1h=-2.649 4h=41.614 | 象限24h=Q2_跌价增仓 1h=Q3_涨价减仓 4h=Q1_涨价增仓 | OI强筛选=Y",
    "结构": "单边偏空 | 突破上=False 跌破=False",
    "周期": "5m:中性/RSI=52.6/纠缠/阴 / 15m:偏空/RSI=50.9/空头排列/阴 / 1h:偏空/RSI=25.5/空头排列/阳 / 4h:偏空/RSI=30.2/空头排列/阳",
    "费率": "短周期OI回落(15m/1h减仓)，垂直下跌后不追空；费率=0.0100%"
  },
  "执行单": {
    "side": "观望",
    "entry": null,
    "stop": null,
    "tp1": null,
    "tp2": null
  },
  "失效条件": "现价不追空；若反抽至1.4265附近且OI再增(Q2)可转做空；失效=收盘站上该反抽高点"
}
```
