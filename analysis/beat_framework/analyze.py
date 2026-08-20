#!/usr/bin/env python3
"""Beat fixed-framework analyzer for xxxUSDT perpetuals.

Usage:
  python3 analysis/beat_framework/analyze.py BEATUSDT
  python3 analysis/beat_framework/analyze.py BTCUSDT --json
  python3 analysis/beat_framework/analyze.py --scan
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

UA = {"User-Agent": "Mozilla/5.0 beat-framework/1.0", "Accept": "application/json"}

# Gate F thresholds (per funding period, as percent)
FUNDING_LONG_CROWDED = 0.05
FUNDING_SHORT_CROWDED = -0.05

# OI strength thresholds (percent change)
OI_STRONG = 3.0
OI_EXTREME = 10.0
OI_EXTREME_5M = 5.0


def classify_oi_strength(
    oi_changes: Dict[str, Optional[float]],
    quadrants: Dict[str, str],
) -> Dict[str, Any]:
    """Grade OI strength. Deleveraging (Q3/Q4) can never be 极强/强."""
    q_primary = quadrants.get("1h") or quadrants.get("15m") or quadrants.get("4h") or "NA"
    q24 = quadrants.get("24h") or q_primary
    vals = {k: oi_changes.get(k) for k in ("5m", "15m", "1h", "4h")}
    build_qs = ("Q1_涨价增仓", "Q2_跌价增仓")
    delev_qs = ("Q3_涨价减仓", "Q4_跌价减仓")

    # 短线正在减仓/去杠杆 → 禁止极强（即使4h历史变动大）
    recent_down = (
        (vals.get("15m") is not None and vals["15m"] < 0)  # type: ignore[index]
        and (vals.get("1h") is not None and vals["1h"] < 0)  # type: ignore[index]
    )
    q_recent = quadrants.get("15m") or quadrants.get("1h") or ""
    recent_delev_quad = q_recent in delev_qs
    # 高周期减仓主导：1h+4h 均为 Q3/Q4 → 禁止用其 |ΔOI| 标强/极强
    higher_delev = (
        quadrants.get("1h") in delev_qs and quadrants.get("4h") in delev_qs
    )

    buildup_24 = q24 in build_qs
    # 当前是否仍在增仓：短线OI为正且为Q1/Q2（5m单独不足，需15m或1h）
    still_building = (
        not recent_down
        and not recent_delev_quad
        and (
            (vals.get("15m") is not None and vals["15m"] > 0 and quadrants.get("15m") in build_qs)
            or (vals.get("1h") is not None and vals["1h"] > 0 and quadrants.get("1h") in build_qs)
        )
    )

    # 强度只统计增仓窗（Q1/Q2 且 ΔOI>0）；减仓窗即使 |ΔOI| 很大也不计入
    abs_build = []
    for k in ("15m", "1h", "4h"):
        v = vals.get(k)
        if v is not None and v > 0 and quadrants.get(k) in build_qs:
            abs_build.append(v)
    max_abs = max(abs_build) if abs_build else 0.0
    v5 = vals.get("5m")
    v5_build = (
        v5 is not None
        and v5 > 0
        and quadrants.get("5m") in build_qs
    )

    if recent_down or recent_delev_quad or higher_delev or not still_building:
        direction = "减仓/去杠杆"
        if "Q3" in (q_recent, q_primary, q24) or quadrants.get("1h") == "Q3_涨价减仓":
            direction = "涨价减仓"
        elif "Q4" in (q_recent, q_primary, q24) or quadrants.get("1h") == "Q4_跌价减仓":
            direction = "跌价减仓"
        elif buildup_24 and q24 == "Q2_跌价增仓":
            direction = "空增仓(已回落)"
        elif buildup_24 and q24 == "Q1_涨价增仓":
            direction = "多增仓(已回落)"
        # 短线微增但高周期已减仓：方向注明，强度仍普通
        if still_building and higher_delev:
            if quadrants.get("15m") == "Q2_跌价增仓" or quadrants.get("5m") == "Q2_跌价增仓":
                direction = "空增仓(短线微增/高周期减仓)"
            elif quadrants.get("15m") == "Q1_涨价增仓" or quadrants.get("5m") == "Q1_涨价增仓":
                direction = "多增仓(短线微增/高周期减仓)"
        level = "普通"
        note = "减仓/去杠杆，大变动不作极强/强"
        buildup = False
        deleveraging = True
    else:
        # 方向取当前增仓象限（优先 15m → 1h → 24h），禁止默认空增仓
        if quadrants.get("15m") in build_qs:
            direction = "多增仓" if quadrants.get("15m") == "Q1_涨价增仓" else "空增仓"
        elif quadrants.get("1h") in build_qs:
            direction = "多增仓" if quadrants.get("1h") == "Q1_涨价增仓" else "空增仓"
        elif q24 == "Q1_涨价增仓":
            direction = "多增仓"
        elif q24 == "Q2_跌价增仓":
            direction = "空增仓"
        else:
            direction = "增仓"
        extreme = max_abs >= OI_EXTREME or (
            v5_build and v5 is not None and abs(v5) >= OI_EXTREME_5M
        )
        strong = max_abs >= OI_STRONG
        if extreme:
            level = "极强"
            note = "OI极强仅作雷达筛选，非开仓许可"
        elif strong:
            level = "强"
            note = "OI强仅作筛选"
        else:
            level = "普通"
            note = ""
        buildup = True
        deleveraging = False

    label = (
        f"OI强度：{level} ＋ {direction} ＋ "
        f"5m={vals.get('5m')} 15m={vals.get('15m')} 1h={vals.get('1h')} 4h={vals.get('4h')}"
    )
    return {
        "level": level,
        "direction": direction,
        "buildup": buildup,
        "deleveraging": deleveraging,
        "label": label,
        "note": note,
        "hint": f"OI提示：{level}（仅雷达，未过闸门不得开仓）" if level == "极强" else "",
    }

def short_term_bear_ema(tf: Dict[str, Any]) -> bool:
    """EMA 空头：15m or 1h price below ema20 and ema20 < ema50 / 空头排列."""
    for key in ("15m", "1h"):
        m = tf.get(key)
        if not m:
            continue
        if m.ma_rel == "空头排列" and m.above_ema20 is False:
            return True
        if m.ema20 is not None and m.ema50 is not None and m.above_ema20 is False and m.ema20 < m.ema50:
            return True
    return False


def short_term_short_buildup(oi_quadrants: Dict[str, str], oi_changes: Dict[str, Optional[float]]) -> bool:
    """短线空增仓：5m/15m Q2, or OI↑ with implied down-move quadrant."""
    for k in ("5m", "15m"):
        if oi_quadrants.get(k) == "Q2_跌价增仓":
            return True
        v = oi_changes.get(k)
        if v is not None and v > 0 and oi_quadrants.get(k) == "Q2_跌价增仓":
            return True
    return False


def oi_divergence_veto(thesis: str, oi_changes: Dict[str, Optional[float]], oi_quadrants: Dict[str, str]) -> Optional[str]:
    """短线 OI 背离一票否决."""
    oi_15 = oi_changes.get("15m")
    oi_1h = oi_changes.get("1h")
    if thesis == "做多":
        # want long buildup; short-term OI falling or Q3 = divergence
        if oi_15 is not None and oi_15 < 0 and oi_1h is not None and oi_1h < 0:
            return "短线OI背离一票否决：欲做多但15m/1h减仓"
        if oi_quadrants.get("15m") == "Q3_涨价减仓":
            return "短线OI背离一票否决：15m涨价减仓"
    if thesis == "做空":
        if oi_15 is not None and oi_15 < 0 and oi_1h is not None and oi_1h < 0:
            return "短线OI背离一票否决：欲做空但15m/1h减仓"
        if oi_quadrants.get("15m") in ("Q4_跌价减仓", "Q3_涨价减仓") and (oi_15 or 0) < 0:
            return "短线OI背离一票否决：短线已去杠杆"
    return None


def tip_chase_veto(chg24: float, pos_pct: Optional[float], thesis: str) -> Optional[str]:
    """tipH/tipL 不追：靠近区间极端或24h暴涨暴跌后不追开."""
    if thesis == "做多":
        if chg24 >= 100:
            return "24h已翻倍→降级观察/止盈，禁止追开"
        if pos_pct is not None and pos_pct >= 92:
            return "tipH不追：价格贴近24h高位"
    if thesis == "做空":
        if chg24 <= -50:
            return "24h深跌后不追空（tipL风险），等反抽"
        if pos_pct is not None and pos_pct <= 8:
            return "tipL不追：价格贴近24h低位"
    return None


def http_get(url: str, timeout: float = 25.0) -> Any:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def safe_get(url: str) -> Tuple[Optional[Any], Optional[str]]:
    try:
        return http_get(url), None
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


def pct(a: float, b: float) -> Optional[float]:
    if b == 0:
        return None
    return (a / b - 1.0) * 100.0


def ema(vals: List[float], n: int) -> List[float]:
    if not vals:
        return []
    k = 2 / (n + 1)
    out = [vals[0]]
    for v in vals[1:]:
        out.append(v * k + out[-1] * (1 - k))
    return out


def rsi(closes: List[float], n: int = 14) -> Optional[float]:
    if len(closes) < n + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    avg_g = sum(gains[-n:]) / n
    avg_l = sum(losses[-n:]) / n
    if avg_l == 0:
        return 100.0
    rs = avg_g / avg_l
    return 100 - (100 / (1 + rs))


def candle_side(o: float, c: float) -> str:
    if c > o:
        return "阳"
    if c < o:
        return "阴"
    return "平"


def quadrant(px_chg: Optional[float], oi_chg: Optional[float]) -> str:
    if px_chg is None or oi_chg is None:
        return "NA"
    if abs(px_chg) < 1e-9 and abs(oi_chg) < 1e-9:
        return "FLAT"
    if px_chg > 0 and oi_chg > 0:
        return "Q1_涨价增仓"
    if px_chg < 0 and oi_chg > 0:
        return "Q2_跌价增仓"
    if px_chg > 0 and oi_chg < 0:
        return "Q3_涨价减仓"
    if px_chg < 0 and oi_chg < 0:
        return "Q4_跌价减仓"
    return "FLAT"


def range_position(last: float, high: float, low: float) -> Optional[float]:
    if high <= low:
        return None
    return (last - low) / (high - low) * 100.0


def is_range(chg24: float, high: float, low: float, last: float) -> bool:
    if abs(chg24) < 2.0:
        return True
    amp = (high - low) / last * 100 if last else 0
    if amp > 0 and abs(chg24) / amp < 0.30:
        return True
    return False


def norm_symbol(raw: str) -> str:
    s = raw.strip().upper().replace("-", "").replace("_", "").replace("/", "")
    if s.endswith("SWAP"):
        s = s[: -len("SWAP")]
    if not s.endswith("USDT"):
        s = s + "USDT"
    return s


def base_of(symbol: str) -> str:
    return symbol[:-4] if symbol.endswith("USDT") else symbol


@dataclass
class VenueQuote:
    venue: str
    last: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    chg24: Optional[float] = None
    funding: Optional[float] = None
    oi_usd: Optional[float] = None
    error: Optional[str] = None


@dataclass
class TfMetrics:
    tf: str
    rsi: Optional[float] = None
    ema20: Optional[float] = None
    ema50: Optional[float] = None
    above_ema20: Optional[bool] = None
    ma_rel: str = "NA"
    candle: str = "NA"
    px_chg: Optional[float] = None
    swing_high: Optional[float] = None
    swing_low: Optional[float] = None
    bias: str = "NA"


@dataclass
class Analysis:
    symbol: str
    ts_utc: str
    quotes: Dict[str, VenueQuote] = field(default_factory=dict)
    oi_changes: Dict[str, Optional[float]] = field(default_factory=dict)
    oi_quadrants: Dict[str, str] = field(default_factory=dict)
    tf: Dict[str, TfMetrics] = field(default_factory=dict)
    structure: Dict[str, Any] = field(default_factory=dict)
    gate_f: Dict[str, Any] = field(default_factory=dict)
    events: Dict[str, Any] = field(default_factory=dict)
    market: Dict[str, Any] = field(default_factory=dict)
    conclusion: str = "观望"
    basis: Dict[str, str] = field(default_factory=dict)
    execution: Dict[str, Any] = field(default_factory=dict)
    invalidation: str = ""
    sources: Dict[str, str] = field(default_factory=dict)


def fetch_gate(symbol: str) -> Tuple[VenueQuote, Dict[str, Any]]:
    contract = f"{base_of(symbol)}_USDT"
    extra: Dict[str, Any] = {"contract": contract}
    q = VenueQuote(venue="Gate")
    data, err = safe_get(f"https://api.gateio.ws/api/v4/futures/usdt/tickers?contract={contract}")
    if err or not data:
        q.error = err or "empty"
        return q, extra
    t = data[0]
    q.last = float(t["last"])
    q.high = float(t["high_24h"])
    q.low = float(t["low_24h"])
    q.chg24 = float(t.get("change_percentage") or 0)
    q.funding = float(t.get("funding_rate") or t.get("funding_rate_indicative") or 0)
    # OI stats multi-interval
    oi_map: Dict[str, Optional[float]] = {}
    for interval, key, need in [("5m", "5m", 2), ("15m", "15m", 2), ("1h", "1h", 2), ("4h", "4h", 2)]:
        # Gate contract_stats: default ~5m; interval param for 1h etc.
        stats, e2 = safe_get(
            f"https://api.gateio.ws/api/v4/futures/usdt/contract_stats?contract={contract}&interval={interval}&limit=30"
        )
        if e2 or not stats or len(stats) < need:
            # fallback without interval for 5m-ish series
            if interval == "5m":
                stats, e2 = safe_get(
                    f"https://api.gateio.ws/api/v4/futures/usdt/contract_stats?contract={contract}&limit=60"
                )
            else:
                oi_map[key] = None
                continue
        if not stats or len(stats) < 2:
            oi_map[key] = None
            continue
        # API returns oldest->newest typically for interval queries; verify
        ordered = sorted(stats, key=lambda x: int(x["time"]))
        bars = {"5m": 1, "15m": 3, "1h": 12, "4h": 48}
        # For interval-native series, compare last vs previous bucket
        if interval in ("1h", "4h", "15m", "5m") and "interval=" in (
            f"interval={interval}"
        ):
            look = {"5m": 1, "15m": 1, "1h": 1, "4h": 1}[interval]
            # Prefer matching wall-clock span using 5m dense series when available
        look_n = bars[key]
        if len(ordered) > look_n:
            oi_now = float(ordered[-1]["open_interest"])
            oi_prev = float(ordered[-1 - look_n]["open_interest"])
            oi_map[key] = pct(oi_now, oi_prev)
            q.oi_usd = float(ordered[-1].get("open_interest_usd") or 0) or q.oi_usd
        elif len(ordered) >= 2:
            oi_map[key] = pct(float(ordered[-1]["open_interest"]), float(ordered[0]["open_interest"]))
            q.oi_usd = float(ordered[-1].get("open_interest_usd") or 0) or q.oi_usd
        else:
            oi_map[key] = None
    # denser 5m series for better multi-horizon OI
    dense, _ = safe_get(
        f"https://api.gateio.ws/api/v4/futures/usdt/contract_stats?contract={contract}&limit=100"
    )
    if dense and len(dense) >= 3:
        ordered = sorted(dense, key=lambda x: int(x["time"]))
        # Gate default stats ~5m
        now = float(ordered[-1]["open_interest"])
        q.oi_usd = float(ordered[-1].get("open_interest_usd") or 0) or q.oi_usd
        for key, n in [("5m", 1), ("15m", 3), ("1h", 12), ("4h", 48)]:
            if len(ordered) > n:
                oi_map[key] = pct(now, float(ordered[-1 - n]["open_interest"]))
    extra["oi_changes"] = oi_map

    # candles for TFs
    candles: Dict[str, List[dict]] = {}
    for interval, lim in [("5m", 80), ("15m", 80), ("1h", 80), ("4h", 80)]:
        rows, e3 = safe_get(
            f"https://api.gateio.ws/api/v4/futures/usdt/candlesticks?contract={contract}&interval={interval}&limit={lim}"
        )
        if e3 or not rows:
            candles[interval] = []
            continue
        # Gate candle keys o,h,l,c,t,v
        ordered = sorted(rows, key=lambda x: int(x["t"]))
        candles[interval] = ordered
    extra["candles"] = candles
    return q, extra


def fetch_okx(symbol: str) -> Tuple[VenueQuote, Dict[str, Any]]:
    inst = f"{base_of(symbol)}-USDT-SWAP"
    q = VenueQuote(venue="OKX")
    extra: Dict[str, Any] = {"instId": inst}
    t, err = safe_get(f"https://www.okx.com/api/v5/market/ticker?instId={inst}")
    if err or not t or not t.get("data"):
        q.error = err or "empty"
        return q, extra
    d = t["data"][0]
    q.last = float(d["last"])
    q.high = float(d["high24h"])
    q.low = float(d["low24h"])
    open24 = float(d.get("open24h") or 0)
    q.chg24 = pct(q.last, open24) if open24 else None
    fr, _ = safe_get(f"https://www.okx.com/api/v5/public/funding-rate?instId={inst}")
    if fr and fr.get("data"):
        q.funding = float(fr["data"][0]["fundingRate"])
    oi_map: Dict[str, Optional[float]] = {}
    for period, key, n in [("5m", "5m", 1), ("15m", "15m", 1), ("1H", "1h", 1), ("4H", "4h", 1)]:
        # also compute from denser 5m if needed
        hist, e = safe_get(
            f"https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-history?instId={inst}&period={period}"
        )
        if e or not hist or not hist.get("data") or len(hist["data"]) < 2:
            oi_map[key] = None
            continue
        ordered = sorted(hist["data"], key=lambda x: int(x[0]))
        # [ts, oi, oiCcy, oiUsd]
        oi_map[key] = pct(float(ordered[-1][2]), float(ordered[-1 - n][2])) if len(ordered) > n else pct(
            float(ordered[-1][2]), float(ordered[0][2])
        )
        q.oi_usd = float(ordered[-1][3])
    # improve with 5m denser
    hist5, _ = safe_get(
        f"https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-history?instId={inst}&period=5m"
    )
    if hist5 and hist5.get("data"):
        ordered = sorted(hist5["data"], key=lambda x: int(x[0]))
        now = float(ordered[-1][2])
        q.oi_usd = float(ordered[-1][3])
        for key, n in [("5m", 1), ("15m", 3), ("1h", 12), ("4h", 48)]:
            if len(ordered) > n:
                oi_map[key] = pct(now, float(ordered[-1 - n][2]))
    extra["oi_changes"] = oi_map
    return q, extra


def fetch_mexc(symbol: str) -> VenueQuote:
    sym = f"{base_of(symbol)}_USDT"
    q = VenueQuote(venue="MEXC")
    t, err = safe_get(f"https://contract.mexc.com/api/v1/contract/ticker?symbol={sym}")
    if err or not t or not t.get("data"):
        q.error = err or "empty"
        return q
    d = t["data"] if isinstance(t["data"], dict) else t["data"][0]
    q.last = float(d["lastPrice"])
    q.high = float(d["high24Price"])
    q.low = float(d["lower24Price"])
    q.chg24 = float(d.get("riseFallRate") or 0) * 100
    q.oi_usd = float(d.get("holdVol") or 0) * q.last  # approx notional
    fr, _ = safe_get(f"https://contract.mexc.com/api/v1/contract/funding_rate/{sym}")
    if fr and fr.get("data"):
        q.funding = float(fr["data"]["fundingRate"])
    return q


def fetch_binance(symbol: str) -> VenueQuote:
    q = VenueQuote(venue="Binance")
    t, err = safe_get(f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}")
    if err:
        q.error = err
        return q
    q.last = float(t["lastPrice"])
    q.high = float(t["highPrice"])
    q.low = float(t["lowPrice"])
    q.chg24 = float(t["priceChangePercent"])
    fr, e2 = safe_get(f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}")
    if not e2 and fr:
        q.funding = float(fr.get("lastFundingRate") or 0)
    return q


def fetch_bybit(symbol: str) -> VenueQuote:
    q = VenueQuote(venue="Bybit")
    t, err = safe_get(f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}")
    if err:
        q.error = err
        return q
    if not t or t.get("retCode") != 0 or not t.get("result", {}).get("list"):
        q.error = "empty"
        return q
    d = t["result"]["list"][0]
    q.last = float(d["lastPrice"])
    q.high = float(d["highPrice24h"])
    q.low = float(d["lowPrice24h"])
    q.chg24 = float(d.get("price24hPcnt") or 0) * 100
    q.funding = float(d.get("fundingRate") or 0)
    q.oi_usd = float(d.get("openInterestValue") or 0) or None
    return q


def tf_metrics_from_candles(tf: str, rows: List[dict]) -> TfMetrics:
    m = TfMetrics(tf=tf)
    if len(rows) < 20:
        return m
    closes = [float(r["c"]) for r in rows]
    highs = [float(r["h"]) for r in rows]
    lows = [float(r["l"]) for r in rows]
    o = float(rows[-1]["o"])
    c = float(rows[-1]["c"])
    m.candle = candle_side(o, c)
    m.rsi = rsi(closes, 14)
    e20 = ema(closes, 20)
    e50 = ema(closes, 50) if len(closes) >= 50 else ema(closes, 20)
    m.ema20 = e20[-1]
    m.ema50 = e50[-1]
    m.above_ema20 = c > e20[-1]
    if e20[-1] > e50[-1] and c > e20[-1]:
        m.ma_rel = "多头排列"
    elif e20[-1] < e50[-1] and c < e20[-1]:
        m.ma_rel = "空头排列"
    else:
        m.ma_rel = "纠缠"
    # price change over window (~12 bars)
    look = min(12, len(closes) - 1)
    m.px_chg = pct(closes[-1], closes[-1 - look])
    m.swing_high = max(highs[-12:])
    m.swing_low = min(lows[-12:])
    # bias
    if m.ma_rel == "多头排列" and (m.rsi or 50) >= 45:
        m.bias = "偏多"
    elif m.ma_rel == "空头排列" and (m.rsi or 50) <= 55:
        m.bias = "偏空"
    else:
        m.bias = "中性"
    return m


def structure_from_tfs(tfs: Dict[str, TfMetrics], chg24: float, high: float, low: float, last: float) -> Dict[str, Any]:
    biases = [tfs[k].bias for k in ("5m", "15m", "1h", "4h") if k in tfs]
    range_flag = is_range(chg24, high, low, last)
    # breakout checks vs 1h swings
    h1 = tfs.get("1h")
    broke_up = bool(h1 and h1.swing_high and last >= h1.swing_high * 0.999)
    broke_dn = bool(h1 and h1.swing_low and last <= h1.swing_low * 1.001)
    if range_flag:
        regime = "震荡RANGE"
    elif chg24 > 0 and biases.count("偏多") >= 2:
        regime = "单边偏多"
    elif chg24 < 0 and biases.count("偏空") >= 2:
        regime = "单边偏空"
    else:
        regime = "结构分歧"
    return {
        "regime": regime,
        "is_range": range_flag,
        "swing_high_1h": h1.swing_high if h1 else None,
        "swing_low_1h": h1.swing_low if h1 else None,
        "break_up": broke_up,
        "break_down": broke_dn,
        "pos_pct": range_position(last, high, low),
    }


def apply_gate_f(thesis: str, funding_pct: Optional[float]) -> Dict[str, Any]:
    if funding_pct is None:
        return {"pass": False, "note": "费率缺失→F无法验证", "funding_pct": None}
    if thesis == "做多" and funding_pct > FUNDING_LONG_CROWDED:
        return {"pass": False, "note": f"F失败:多头拥挤 {funding_pct:.4f}%", "funding_pct": funding_pct}
    if thesis == "做空" and funding_pct < FUNDING_SHORT_CROWDED:
        return {"pass": False, "note": f"F失败:空头拥挤 {funding_pct:.4f}%", "funding_pct": funding_pct}
    return {"pass": True, "note": f"F过闸 费率={funding_pct:.4f}%", "funding_pct": funding_pct}


def decide(a: Analysis) -> None:
    # pick primary quote: prefer Gate > OKX > MEXC > Bybit > Binance
    primary = None
    for name in ("Gate", "OKX", "MEXC", "Bybit", "Binance"):
        q = a.quotes.get(name)
        if q and q.last is not None and not q.error:
            primary = q
            break
    if not primary:
        a.conclusion = "观望"
        a.basis = {"价格": "无可用行情"}
        a.invalidation = "数据恢复前不交易"
        return

    last = primary.last or 0.0
    high = primary.high or last
    low = primary.low or last
    chg24 = primary.chg24 or 0.0
    funding_pct = (primary.funding or 0.0) * 100

    q1h = a.oi_quadrants.get("1h", "NA")
    q4h = a.oi_quadrants.get("4h", "NA")
    oi_1h = a.oi_changes.get("1h")
    oi_4h = a.oi_changes.get("4h")
    oi_15m = a.oi_changes.get("15m")

    oi_for_24h = oi_4h if oi_4h is not None else oi_1h
    q24 = quadrant(chg24, oi_for_24h)
    a.oi_quadrants["24h"] = q24
    a.oi_changes["24h_proxy"] = oi_for_24h

    # Align 24h dump/pump with OI buildup
    if chg24 < -5 and oi_for_24h is not None and oi_for_24h > 3:
        q24 = "Q2_跌价增仓"
        a.oi_quadrants["24h"] = q24
    if chg24 > 5 and oi_for_24h is not None and oi_for_24h > 3:
        q24 = "Q1_涨价增仓"
        a.oi_quadrants["24h"] = q24

    oi_grade = classify_oi_strength(a.oi_changes, a.oi_quadrants)
    a.structure["oi_grade"] = oi_grade

    struct = a.structure
    pos_pct = struct.get("pos_pct")
    thesis = "观望"
    veto_notes: List[str] = []
    extreme_watch = False  # 极强但观望

    if struct.get("is_range"):
        veto_notes.append("RANGE不当单边")
    else:
        # 以24h象限为主；单根4h阳线反弹造成的Q1不得在大跌日触发开多候选
        long_oi = q24 == "Q1_涨价增仓" or (
            chg24 > 0 and (q1h == "Q1_涨价增仓" or q4h == "Q1_涨价增仓")
        )
        short_oi = q24 == "Q2_跌价增仓" or (
            chg24 < 0 and (q1h == "Q2_跌价增仓" or q4h == "Q2_跌价增仓")
        )
        # 若24h已强制对齐，覆盖
        if q24 == "Q1_涨价增仓":
            long_oi, short_oi = True, False
        elif q24 == "Q2_跌价增仓":
            long_oi, short_oi = False, True
        still_long_build = long_oi and (oi_15m is None or oi_15m >= 0) and (oi_1h is None or oi_1h >= 0)
        still_short_build = short_oi and (oi_15m is None or oi_15m >= 0) and (oi_1h is None or oi_1h >= -0.5)

        structure_up = struct.get("regime") == "单边偏多" or bool(struct.get("break_up"))
        structure_dn = struct.get("regime") == "单边偏空" or bool(struct.get("break_down"))
        ema_bear = short_term_bear_ema(a.tf)
        st_short_build = short_term_short_buildup(a.oi_quadrants, a.oi_changes)

        # --- 开多硬闸门 ---
        # 1) 短线空增仓 / EMA空头 → 默认观望，不给现价多
        can_long = True
        if st_short_build or ema_bear:
            can_long = False
            if long_oi or struct.get("regime") == "单边偏多":
                veto_notes.append("短线空增仓或EMA空头→禁止现价多，默认观望")
        # 2) 必须结构UP或突破确认 + OI仍多增仓
        if long_oi and not (structure_up and still_long_build):
            can_long = False
            veto_notes.append("开多未满足：需结构UP/突破确认且OI仍多增仓")
        if not long_oi:
            can_long = False

        # --- 开空硬闸门（对称，tipL另判）---
        can_short = bool(structure_dn and still_short_build and short_oi)
        if short_oi and not can_short:
            veto_notes.append("开空未满足：需结构DOWN/跌破且OI仍空增仓（短线减仓不追）")

        if can_long and long_oi and structure_up:
            thesis = "做多"
        elif can_short:
            thesis = "做空"
        else:
            thesis = "观望"

        # 短线 OI 背离一票否决
        if thesis in ("做多", "做空"):
            div = oi_divergence_veto(thesis, a.oi_changes, a.oi_quadrants)
            if div:
                veto_notes.append(div)
                thesis = "观望"

        # tipH/tipL 不追 + 24h翻倍降级
        if thesis in ("做多", "做空"):
            tip = tip_chase_veto(chg24, pos_pct, thesis)
            if tip:
                veto_notes.append(tip)
                thesis = "观望"

        # 结构硬否决
        if thesis == "做多" and struct.get("regime") == "单边偏空":
            veto_notes.append("结构空头否决做多")
            thesis = "观望"
        if thesis == "做空" and struct.get("regime") == "单边偏多":
            veto_notes.append("结构多头否决做空")
            thesis = "观望"

        # 闸门 F
        if thesis in ("做多", "做空"):
            a.gate_f = apply_gate_f(thesis, funding_pct)
            if not a.gate_f["pass"]:
                veto_notes.append(a.gate_f.get("note", "F失败"))
                thesis = "观望"
        else:
            a.gate_f = {
                "pass": False,
                "note": "；".join(veto_notes) if veto_notes else f"无开仓许可 24h象限={q24}",
                "funding_pct": funding_pct,
            }

    # TF soft veto
    biases = [a.tf[k].bias for k in ("5m", "15m", "1h", "4h") if k in a.tf]
    if thesis == "做多" and biases.count("偏空") >= 3:
        veto_notes.append("多周期偏空否决")
        thesis = "观望"
    if thesis == "做空" and biases.count("偏多") >= 3:
        veto_notes.append("多周期偏多否决")
        thesis = "观望"

    # 极强仍要过结构/背离闸门；未过 → 极强但观望
    if thesis == "观望" and oi_grade.get("level") == "极强" and oi_grade.get("buildup"):
        extreme_watch = True
        a.conclusion = "极强但观望"
    else:
        a.conclusion = thesis

    if veto_notes:
        a.gate_f = a.gate_f or {}
        a.gate_f["pass"] = thesis in ("做多", "做空")
        a.gate_f["funding_pct"] = funding_pct
        prev = a.gate_f.get("note") or ""
        merged = "；".join(dict.fromkeys([*(prev.split("；") if prev else []), *veto_notes]))
        a.gate_f["note"] = merged

    # Execution
    m15 = a.tf.get("15m")
    atr_proxy = None
    if m15 and m15.swing_high and m15.swing_low:
        atr_proxy = (m15.swing_high - m15.swing_low) / 4.0
    if not atr_proxy or atr_proxy <= 0:
        atr_proxy = last * 0.01

    if thesis == "做空":
        entry = last
        sl = min(m15.swing_high, entry + 1.5 * atr_proxy) if m15 and m15.swing_high else entry + 1.5 * atr_proxy
        if sl > entry * 1.08:
            sl = entry + 1.5 * atr_proxy
        risk = max(sl - entry, last * 0.005)
        a.execution = {
            "side": "做空",
            "entry": round(entry, 6),
            "stop": round(sl, 6),
            "tp1": round(entry - 1.5 * risk, 6),
            "tp2": round(entry - 2.5 * risk, 6),
        }
        a.invalidation = f"15m/1H收盘站上{round(sl,6)}，或转为Q4跌价减仓且波动收敛"
    elif thesis == "做多":
        entry = last
        sl = max(m15.swing_low, entry - 1.5 * atr_proxy) if m15 and m15.swing_low else entry - 1.5 * atr_proxy
        if sl < entry * 0.92:
            sl = entry - 1.5 * atr_proxy
        risk = max(entry - sl, last * 0.005)
        a.execution = {
            "side": "做多",
            "entry": round(entry, 6),
            "stop": round(sl, 6),
            "tp1": round(entry + 1.5 * risk, 6),
            "tp2": round(entry + 2.5 * risk, 6),
        }
        a.invalidation = f"15m/1H收盘跌破{round(sl,6)}，或转为Q3涨价减仓"
    else:
        a.execution = {"side": "观望", "entry": None, "stop": None, "tp1": None, "tp2": None}
        a.invalidation = "需结构UP/DOWN确认 + OI仍同向增仓 + 过闸门F；tipH/tipL不追"

    oi_line = oi_grade["label"]
    if oi_grade.get("hint"):
        oi_line += f" | {oi_grade['hint']}"
    if oi_grade.get("note") and oi_grade["level"] == "普通" and oi_grade.get("deleveraging"):
        oi_line += f" | {oi_grade['note']}"

    a.basis = {
        "价格": f"主源{primary.venue} {last} | 24h {chg24:.2f}% | 高{high} 低{low} | 位置{pos_pct:.1f}%"
        if pos_pct is not None
        else f"主源{primary.venue} {last} | 24h {chg24:.2f}%",
        "OI": oi_line + f" | 象限24h={a.oi_quadrants.get('24h')} 1h={q1h} 4h={q4h}",
        "结构": f"{struct.get('regime')} | 突破上={struct.get('break_up')} 跌破={struct.get('break_down')}"
        + (" | 极强但观望" if extreme_watch else ""),
        "周期": " / ".join(
            f"{k}:{a.tf[k].bias}/RSI={None if a.tf[k].rsi is None else round(a.tf[k].rsi,1)}/{a.tf[k].ma_rel}/{a.tf[k].candle}"
            for k in ("5m", "15m", "1h", "4h")
            if k in a.tf
        ),
        "费率": (a.gate_f or {}).get("note", ""),
    }
    if a.conclusion in ("观望", "极强但观望") and chg24 < -20 and struct.get("regime") == "单边偏空":
        trigger = round(m15.swing_high, 6) if m15 and m15.swing_high else round(last * 1.04, 6)
        a.invalidation = (
            f"现价不追；若反抽至{trigger}附近且OI再增(Q2)可评估做空；失效=收盘站上该反抽高点"
        )


def fetch_events(symbol: str) -> Dict[str, Any]:
    base = base_of(symbol)
    out: Dict[str, Any] = {
        "cryptopanic": None,
        "fear_greed": None,
        "onchain": "N/A（当前环境无稳定链上接口）",
        "whales": "N/A（当前环境无大额转账接口）",
        "social": "N/A",
        "news": [],
    }
    # CryptoPanic
    cp, err = safe_get(
        f"https://cryptopanic.com/api/v1/posts/?auth_token=free&public=true&currencies={base}"
    )
    if err:
        out["cryptopanic"] = f"N/A ({err})"
    else:
        out["cryptopanic"] = cp

    fng, err2 = safe_get("https://api.alternative.me/fng/?limit=1")
    if not err2 and fng and fng.get("data"):
        out["fear_greed"] = {
            "value": fng["data"][0]["value"],
            "class": fng["data"][0]["value_classification"],
        }
    else:
        out["fear_greed"] = f"N/A ({err2})"

    # Coingecko trending as soft sentiment proxy
    cg, err3 = safe_get("https://api.coingecko.com/api/v3/search/trending")
    if not err3 and cg:
        coins = [x.get("item", {}).get("symbol") for x in cg.get("coins", [])]
        out["news"].append({"source": "coingecko_trending", "symbols": coins[:10]})
        out["social"] = f"CoinGecko trending含{base}={base in coins}" if coins else "N/A"
    return out


def fetch_market_context() -> Dict[str, Any]:
    ctx: Dict[str, Any] = {}
    for sym, key in [("BTCUSDT", "BTC"), ("ETHUSDT", "ETH")]:
        g, extra = fetch_gate(sym)
        ctx[key] = {
            "venue": "Gate" if g.last is not None else None,
            "last": g.last,
            "chg24": g.chg24,
            "funding_pct": None if g.funding is None else g.funding * 100,
            "is_range": is_range(g.chg24 or 0, g.high or 0, g.low or 0, g.last or 1) if g.last else None,
            "error": g.error,
            "oi_1h": (extra.get("oi_changes") or {}).get("1h"),
        }
    return ctx


def analyze_symbol(symbol: str, with_events: bool = True) -> Analysis:
    symbol = norm_symbol(symbol)
    a = Analysis(symbol=symbol, ts_utc=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))

    gate_q, gate_x = fetch_gate(symbol)
    a.quotes["Gate"] = gate_q
    a.sources["Gate"] = "OK" if gate_q.last is not None else f"N/A:{gate_q.error}"

    okx_q, okx_x = fetch_okx(symbol)
    a.quotes["OKX"] = okx_q
    a.sources["OKX"] = "OK" if okx_q.last is not None else f"N/A:{okx_q.error}"

    mexc_q = fetch_mexc(symbol)
    a.quotes["MEXC"] = mexc_q
    a.sources["MEXC"] = "OK" if mexc_q.last is not None else f"N/A:{mexc_q.error}"

    byb = fetch_bybit(symbol)
    a.quotes["Bybit"] = byb
    a.sources["Bybit"] = "OK" if byb.last is not None else f"N/A:{byb.error}"

    bnc = fetch_binance(symbol)
    a.quotes["Binance"] = bnc
    a.sources["Binance"] = "OK" if bnc.last is not None else f"N/A:{bnc.error}"

    # Prefer OKX OI (cleaner multi-TF), else Gate
    oi = okx_x.get("oi_changes") or gate_x.get("oi_changes") or {}
    a.oi_changes = {k: (None if v is None else round(v, 3)) for k, v in oi.items()}

    # price changes per TF from Gate candles
    candles = gate_x.get("candles") or {}
    px_chg: Dict[str, Optional[float]] = {}
    for tf in ("5m", "15m", "1h", "4h"):
        rows = candles.get(tf) or []
        a.tf[tf] = tf_metrics_from_candles(tf, rows)
        if len(rows) >= 2:
            look = {"5m": 1, "15m": 1, "1h": 1, "4h": 1}[tf]
            # use ~ equivalent horizon on same TF series: last vs 1 bar for native; better use fixed bars
            bars = {"5m": 1, "15m": 1, "1h": 1, "4h": 1}[tf]
            px_chg[tf] = pct(float(rows[-1]["c"]), float(rows[-1 - bars]["c"])) if len(rows) > bars else None
        else:
            px_chg[tf] = a.tf[tf].px_chg
        a.oi_quadrants[tf] = quadrant(px_chg.get(tf), a.oi_changes.get(tf))

    # structure using primary gate/okx
    primary = gate_q if gate_q.last is not None else okx_q
    if primary.last is not None:
        a.structure = structure_from_tfs(
            a.tf, primary.chg24 or 0.0, primary.high or primary.last, primary.low or primary.last, primary.last
        )
    else:
        a.structure = {"regime": "NA", "is_range": True}

    if with_events:
        a.events = fetch_events(symbol)
        a.market = fetch_market_context()

    decide(a)
    return a


def to_dict(a: Analysis) -> Dict[str, Any]:
    return {
        "symbol": a.symbol,
        "ts_utc": a.ts_utc,
        "sources": a.sources,
        "quotes": {k: v.__dict__ for k, v in a.quotes.items()},
        "oi_changes": a.oi_changes,
        "oi_quadrants": a.oi_quadrants,
        "structure": a.structure,
        "tf": {k: v.__dict__ for k, v in a.tf.items()},
        "gate_f": a.gate_f,
        "events": a.events,
        "market": a.market,
        "结论": a.conclusion,
        "依据": a.basis,
        "执行单": a.execution,
        "失效条件": a.invalidation,
    }


def format_report(a: Analysis) -> str:
    lines: List[str] = []
    lines.append(f"# {a.symbol} Beat固定框架报告")
    lines.append(f"- 时间：{a.ts_utc}")
    lines.append(f"- 数据源：{a.sources}")
    lines.append("")
    lines.append("## 统一结论")
    lines.append(f"•结论：{a.conclusion}")
    lines.append("•依据：")
    for k, v in a.basis.items():
        lines.append(f"  - {k}：{v}")
    exe = a.execution
    if exe.get("side") == "观望":
        lines.append("•执行单：观望（不下手）")
    else:
        lines.append(
            f"•执行单：{exe.get('side')} / 入场 {exe.get('entry')} / 止损 {exe.get('stop')} / 止盈 {exe.get('tp1')} → {exe.get('tp2')}"
        )
    lines.append(f"•失效条件：{a.invalidation}")
    lines.append("")
    lines.append("## 1 交易行情·现价")
    lines.append("|交易所|现价|24h高|24h低|涨跌%|位置%|费率%|状态|")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for name, q in a.quotes.items():
        if q.error and q.last is None:
            lines.append(f"|{name}|N/A|N/A|N/A|N/A|N/A|N/A|{q.error}|")
            continue
        pos = range_position(q.last or 0, q.high or 0, q.low or 0)
        lines.append(
            f"|{name}|{q.last}|{q.high}|{q.low}|{None if q.chg24 is None else round(q.chg24,2)}|"
            f"{None if pos is None else round(pos,1)}|{None if q.funding is None else round(q.funding*100,4)}|OK|"
        )
    lines.append("")
    lines.append("## 2 OI四象限")
    lines.append("|周期|ΔOI%|象限|")
    lines.append("|---|---:|---|")
    for tf in ("5m", "15m", "1h", "4h"):
        lines.append(f"|{tf}|{a.oi_changes.get(tf)}|{a.oi_quadrants.get(tf)}|")
    lines.append("")
    lines.append("## 3 结构")
    lines.append(json.dumps(a.structure, ensure_ascii=False))
    lines.append("")
    lines.append("## 4 周期 RSI/均线/阴阳")
    lines.append("|周期|RSI|均线|阴阳|偏向|")
    lines.append("|---|---:|---|---|---|")
    for tf in ("5m", "15m", "1h", "4h"):
        m = a.tf.get(tf)
        if not m:
            continue
        lines.append(
            f"|{tf}|{None if m.rsi is None else round(m.rsi,1)}|{m.ma_rel}|{m.candle}|{m.bias}|"
        )
    lines.append("")
    lines.append("## 5 资金费率 / 闸门F")
    lines.append(json.dumps(a.gate_f, ensure_ascii=False))
    lines.append("")
    lines.append("## 6 事件 / 舆情 / 链上 / 大额转账")
    ev = a.events or {}
    lines.append(f"- CryptoPanic：{ev.get('cryptopanic')}")
    lines.append(f"- 舆情/社交：{ev.get('social')}")
    lines.append(f"- 链上：{ev.get('onchain')}")
    lines.append(f"- 大额转账：{ev.get('whales')}")
    lines.append(f"- Fear&Greed：{ev.get('fear_greed')}")
    lines.append("")
    lines.append("## 7 市场环境")
    lines.append(json.dumps(a.market, ensure_ascii=False))
    lines.append("")
    return "\n".join(lines)


def scan_oi_candidates(min_quote_vol: float = 20_000_000) -> List[Dict[str, Any]]:
    """Scan Gate tickers for strong OI one-sided candidates, then gate F + RANGE."""
    data, err = safe_get("https://api.gateio.ws/api/v4/futures/usdt/tickers")
    if err or not data:
        return [{"error": err or "empty"}]
    cands = []
    for t in data:
        try:
            last = float(t["last"])
            vol = float(t.get("volume_24h_quote") or t.get("volume_24h_settle") or 0)
            if vol < min_quote_vol:
                # fallback approximate
                vol = float(t.get("volume_24h_base") or 0) * last
            if vol < min_quote_vol:
                continue
            chg = float(t.get("change_percentage") or 0)
            high = float(t["high_24h"])
            low = float(t["low_24h"])
            if is_range(chg, high, low, last):
                continue
            cands.append(t["contract"])
        except Exception:  # noqa: BLE001
            continue
    # Limit deep analysis to top movers by abs chg
    cands = sorted(
        cands,
        key=lambda c: abs(float(next(x for x in data if x["contract"] == c).get("change_percentage") or 0)),
        reverse=True,
    )[:18]

    results = []
    for contract in cands:
        sym = contract.replace("_", "")
        a = analyze_symbol(sym, with_events=False)
        if a.conclusion in ("做多", "做空", "极强但观望"):
            results.append(
                {
                    "symbol": a.symbol,
                    "结论": a.conclusion,
                    "依据": a.basis,
                    "执行单": a.execution,
                    "失效条件": a.invalidation,
                    "oi": a.oi_changes,
                    "quad": a.oi_quadrants,
                    "oi_grade": (a.structure or {}).get("oi_grade"),
                }
            )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Beat fixed-framework xxxUSDT analyzer")
    parser.add_argument("symbol", nargs="?", default="BEATUSDT", help="e.g. BEATUSDT")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--scan", action="store_true", help="Scan OI one-sided candidates")
    parser.add_argument("--out", default="", help="Write report path")
    args = parser.parse_args()

    if args.scan:
        rows = scan_oi_candidates()
        text = json.dumps(rows, ensure_ascii=False, indent=2)
        print(text)
        out = args.out or f"analysis/reports/scan_{int(time.time())}.json"
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\n[wrote] {out}", file=sys.stderr)
        return 0

    a = analyze_symbol(args.symbol, with_events=True)
    payload = to_dict(a)
    report = format_report(a)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(report)

    out = args.out or f"analysis/reports/{a.symbol}_{int(time.time())}.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(report)
        f.write("\n\n```json\n")
        f.write(json.dumps(payload, ensure_ascii=False, indent=2))
        f.write("\n```\n")
    print(f"\n[wrote] {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
