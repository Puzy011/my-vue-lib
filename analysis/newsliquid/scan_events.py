#!/usr/bin/env python3
"""newsliquid MVP scanner: OI_SPIKE + OI_CONCENTRATION → observe pool only.

Never auto-opens trades. WHALE_PNL_START is emitted as blocked without a paid source.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

UA = {"User-Agent": "Mozilla/5.0 newsliquid/1.0", "Accept": "application/json"}

# Thresholds
OI_SPIKE_5M = 5.0
OI_SPIKE_15M = 8.0
OI_SPIKE_1H = 10.0
CONCENTRATION_PCT = 50.0
MIN_QUOTE_VOL = 5_000_000
COOLDOWN_SEC = 900
DEFAULT_COOLDOWN_STATE = "analysis/newsliquid/watch_pool/cooldown.json"


def http_get(url: str, timeout: float = 25.0) -> Any:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def safe_get(url: str) -> Tuple[Optional[Any], Optional[str]]:
    try:
        return http_get(url), None
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def bucket_ts(sec: int = 300) -> int:
    return int(time.time()) // sec * sec


def load_cooldown(path: str) -> Dict[str, float]:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return {}


def save_cooldown(path: str, state: Dict[str, float]) -> None:
    import os

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)


def in_cooldown(state: Dict[str, float], key: str, cooldown: int = COOLDOWN_SEC) -> bool:
    last = state.get(key)
    if last is None:
        return False
    return (time.time() - last) < cooldown


def pct(a: float, b: float) -> Optional[float]:
    if b == 0:
        return None
    return (a / b - 1.0) * 100.0


def make_event(
    event_type: str,
    symbol: str,
    venue: str,
    side_bias: str,
    payload: Dict[str, Any],
    thresholds: Dict[str, Any],
    gates_hint: Dict[str, Any],
    severity: str = "watch",
    severity_reason: str = "仅观察池",
    tf: str = "15m",
) -> Dict[str, Any]:
    bts = bucket_ts()
    dedupe = f"{event_type}:{symbol}:{side_bias}:{tf}"
    return {
        "event_id": f"{event_type}:{symbol}:{bts}",
        "event_type": event_type,
        "symbol": symbol,
        "ts_utc": utc_now(),
        "venue": venue,
        "side_bias": side_bias,
        "severity": severity,
        "severity_reason": severity_reason,
        "dedupe_key": dedupe,
        "cooldown_sec": COOLDOWN_SEC,
        "pool": "observe",
        "thresholds": thresholds,
        "payload": payload,
        "gates_hint": gates_hint,
    }


def oi_strength_from_chg(oi_chg: float) -> str:
    a = abs(oi_chg)
    if a >= 10:
        return "极强"
    if a >= 3:
        return "强"
    return "普通"


def scan_gate_universe(limit: int = 40) -> List[dict]:
    data, err = safe_get("https://api.gateio.ws/api/v4/futures/usdt/tickers")
    if err or not data:
        return []
    rows = []
    for t in data:
        try:
            last = float(t["last"])
            vol = float(t.get("volume_24h_quote") or 0)
            if vol <= 0:
                vol = float(t.get("volume_24h_base") or 0) * last
            if vol < MIN_QUOTE_VOL:
                continue
            chg = abs(float(t.get("change_percentage") or 0))
            rows.append((chg, t))
        except Exception:  # noqa: BLE001
            continue
    rows.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in rows[:limit]]


def analyze_contract(ticker: dict) -> List[Dict[str, Any]]:
    contract = ticker["contract"]
    symbol = contract.replace("_", "")
    last = float(ticker["last"])
    chg24 = float(ticker.get("change_percentage") or 0)
    high = float(ticker["high_24h"])
    low = float(ticker["low_24h"])
    funding = float(ticker.get("funding_rate") or ticker.get("funding_rate_indicative") or 0) * 100
    pos = ((last - low) / (high - low) * 100) if high > low else None

    events: List[Dict[str, Any]] = []

    # Dense ~5m stats for OI spike
    stats, err = safe_get(
        f"https://api.gateio.ws/api/v4/futures/usdt/contract_stats?contract={contract}&limit=80"
    )
    if err or not stats or len(stats) < 5:
        return events
    ordered = sorted(stats, key=lambda x: int(x["time"]))
    oi_now = float(ordered[-1]["open_interest"])
    oi_usd = float(ordered[-1].get("open_interest_usd") or 0)
    top_long = float(ordered[-1].get("top_long_size") or 0)
    top_short = float(ordered[-1].get("top_short_size") or 0)

    windows = [("5m", 1, OI_SPIKE_5M), ("15m", 3, OI_SPIKE_15M), ("1h", 12, OI_SPIKE_1H)]
    for tf, n, thr in windows:
        if len(ordered) <= n:
            continue
        oi_prev = float(ordered[-1 - n]["open_interest"])
        oi_chg = pct(oi_now, oi_prev)
        if oi_chg is None or oi_chg <= 0:
            continue  # 减仓不作 SPIKE 增仓事件
        if oi_chg < thr:
            continue
        # price change over same span via mark_price
        px_now = float(ordered[-1].get("mark_price") or last)
        px_prev = float(ordered[-1 - n].get("mark_price") or last)
        px_chg = pct(px_now, px_prev) or 0.0
        if px_chg > 0:
            quad = "Q1_涨价增仓"
            side = "long_build"
        elif px_chg < 0:
            quad = "Q2_跌价增仓"
            side = "short_build"
        else:
            continue

        severity = "watch"
        reason = "短窗OI异动+增仓象限，仅观察池"
        tip_risk = False
        if chg24 >= 100 or (pos is not None and pos >= 92 and side == "long_build"):
            severity = "observe_take_profit"
            reason = "24h翻倍或tipH→降级观察/止盈，禁止追开"
            tip_risk = True
        if chg24 <= -50 or (pos is not None and pos <= 8 and side == "short_build"):
            severity = "observe_take_profit"
            reason = "深跌tipL→降级观察，禁止追空"
            tip_risk = True
        if (side == "long_build" and funding > 0.05) or (side == "short_build" and funding < -0.05):
            severity = "observe_take_profit"
            reason = "费率拥挤→降级观察/止盈，禁止追开"

        events.append(
            make_event(
                "OI_SPIKE",
                symbol,
                "Gate",
                side,
                {
                    "tf": tf,
                    "oi_chg_pct": round(oi_chg, 3),
                    "px_chg_pct": round(px_chg, 3),
                    "quadrant": quad,
                    "oi_usd": oi_usd,
                },
                {"oi_chg_5m_pct": OI_SPIKE_5M, "oi_chg_15m_pct": OI_SPIKE_15M, "oi_chg_1h_pct": OI_SPIKE_1H},
                {
                    "oi_strength": oi_strength_from_chg(oi_chg),
                    "range_suspected": abs(chg24) < 2,
                    "funding_pct": round(funding, 4),
                    "chg24_pct": round(chg24, 2),
                    "tip_chase_risk": tip_risk,
                    "note": "OI极强≠开仓许可；需结构确认+OI仍同向增仓",
                },
                severity=severity,
                severity_reason=reason,
                tf=tf,
            )
        )
        break  # one SPIKE per symbol per scan (highest tf priority already ordered 5m→1h; keep first hit)

    # Concentration
    if oi_now > 0:
        conc = (top_long + top_short) / oi_now * 100
        if conc >= CONCENTRATION_PCT:
            if top_long > top_short * 1.15:
                dominant = "long"
                side = "long_build"
                aligned = chg24 > 0
            elif top_short > top_long * 1.15:
                dominant = "short"
                side = "short_build"
                aligned = chg24 < 0
            else:
                dominant = "balanced"
                side = "unknown"
                aligned = False
            if aligned and side != "unknown":
                sev = "watch"
                reason = "top持仓集中度过阈且与价格同向，仅观察池"
                if chg24 >= 100 or chg24 <= -50:
                    sev = "observe_take_profit"
                    reason = "已极端波动，集中度事件降级观察/止盈"
                events.append(
                    make_event(
                        "OI_CONCENTRATION",
                        symbol,
                        "Gate",
                        side,
                        {
                            "top_long_size": top_long,
                            "top_short_size": top_short,
                            "open_interest": oi_now,
                            "concentration_pct": round(conc, 2),
                            "dominant_side": dominant,
                            "aligned": aligned,
                            "px_chg_pct": round(chg24, 2),
                        },
                        {"concentration_pct": CONCENTRATION_PCT},
                        {
                            "oi_strength": "强" if conc >= 60 else "普通",
                            "range_suspected": abs(chg24) < 2,
                            "funding_pct": round(funding, 4),
                            "chg24_pct": round(chg24, 2),
                            "tip_chase_risk": abs(chg24) >= 50,
                            "note": "集中度是主力代理，不是开仓许可",
                        },
                        severity=sev,
                        severity_reason=reason,
                        tf="1h",
                    )
                )

    return events


def whale_pnl_placeholder(symbols: List[str]) -> List[Dict[str, Any]]:
    """No paid source → blocked stubs only (do not pretend whale started)."""
    out = []
    for sym in symbols[:3]:
        out.append(
            make_event(
                "WHALE_PNL_START",
                sym,
                "Multi",
                "unknown",
                {"source": None, "available": False, "pnl_slope_turn_positive": False, "position_value_usd": None},
                {},
                {"oi_strength": "普通", "range_suspected": False, "funding_pct": None, "chg24_pct": None, "tip_chase_risk": False, "note": "无PnL源"},
                severity="blocked",
                severity_reason="无付费聪明钱/PnL源，禁止假装主力已启动",
                tf="na",
            )
        )
    return out


def run_once(out_path: str, cooldown_path: str, with_whale_stub: bool = False) -> Dict[str, Any]:
    universe = scan_gate_universe()
    cooldown = load_cooldown(cooldown_path)
    events: List[Dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(analyze_contract, t) for t in universe]
        for fut in as_completed(futs):
            try:
                events.extend(fut.result())
            except Exception:  # noqa: BLE001
                continue

    # dedupe + cooldown
    accepted: List[Dict[str, Any]] = []
    seen = set()
    for ev in events:
        dk = ev["dedupe_key"]
        if dk in seen:
            continue
        seen.add(dk)
        if in_cooldown(cooldown, dk):
            continue
        accepted.append(ev)
        cooldown[dk] = time.time()

    if with_whale_stub and accepted:
        accepted.extend(whale_pnl_placeholder([e["symbol"] for e in accepted]))

    save_cooldown(cooldown_path, cooldown)
    result = {
        "ts_utc": utc_now(),
        "universe": len(universe),
        "emitted": len(accepted),
        "pool": "observe",
        "note": "事件只进观察池；开仓仍过结构/背离/闸门F/tipH·tipL",
        "events": accepted,
    }
    import os

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def main() -> int:
    p = argparse.ArgumentParser(description="newsliquid observe-pool scanner")
    p.add_argument("--once", action="store_true", default=True)
    p.add_argument("--out", default="analysis/newsliquid/watch_pool/latest.json")
    p.add_argument("--cooldown", default=DEFAULT_COOLDOWN_STATE)
    p.add_argument("--whale-stub", action="store_true", help="Emit blocked WHALE_PNL_START stubs")
    args = p.parse_args()
    result = run_once(args.out, args.cooldown, with_whale_stub=args.whale_stub)
    # compact stdout
    summary = [
        {
            "type": e["event_type"],
            "symbol": e["symbol"],
            "severity": e["severity"],
            "side": e["side_bias"],
            "reason": e["severity_reason"],
            "oi_strength": e.get("gates_hint", {}).get("oi_strength"),
            "payload": e.get("payload"),
        }
        for e in result["events"]
        if e["event_type"] != "WHALE_PNL_START"
    ]
    print(json.dumps({"ts": result["ts_utc"], "emitted": result["emitted"], "events": summary}, ensure_ascii=False, indent=2))
    print(f"[wrote] {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
