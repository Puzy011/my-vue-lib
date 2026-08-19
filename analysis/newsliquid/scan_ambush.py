#!/usr/bin/env python3
"""埋伏筛选：即将拉升 / 即将大跌的强庄观察池。

事件只进观察池，不是开仓许可。现价追高/追低一律剔除。
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan_events import (  # noqa: E402
    MIN_QUOTE_VOL,
    analyze_contract,
    scan_gate_universe,
    utc_now,
)

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional


def pos_pct(ticker: dict) -> Optional[float]:
    last = float(ticker["last"])
    high = float(ticker["high_24h"])
    low = float(ticker["low_24h"])
    if high <= low:
        return None
    return (last - low) / (high - low) * 100.0


def event_row(e: Dict[str, Any], ticker: dict, ambush: str) -> Dict[str, Any]:
    gh = e.get("gates_hint") or {}
    payload = e.get("payload") or {}
    last = float(ticker["last"])
    chg = float(ticker.get("change_percentage") or 0)
    pos = pos_pct(ticker)
    return {
        "symbol": e["symbol"],
        "type": e.get("event_type"),
        "side": e.get("side_bias"),
        "severity": e.get("severity"),
        "oi_strength": gh.get("oi_strength"),
        "oi_accel_5m": gh.get("oi_accel_5m"),
        "rescan_priority": gh.get("rescan_priority"),
        "chg24": round(chg, 2),
        "pos": None if pos is None else round(pos, 1),
        "last": last,
        "startup_phase": e.get("startup_phase"),
        "reason": e.get("severity_reason"),
        "payload_brief": {
            k: payload.get(k)
            for k in (
                "concentration_pct",
                "dominant_side",
                "tf",
                "oi_chg_pct",
                "quadrant",
                "oi_chg_5m",
                "oi_chg_15m",
            )
            if k in payload
        },
        "ambush": ambush,
    }


def classify(e: Dict[str, Any], ticker: dict) -> Optional[str]:
    if e.get("severity") in ("blocked", "observe_take_profit"):
        return None
    side = e.get("side_bias")
    chg = float(ticker.get("change_percentage") or 0)
    pos = pos_pct(ticker)
    funding = float((e.get("gates_hint") or {}).get("funding_pct") or 0)
    if pos is None:
        return None
    # 拉升埋伏：多头集中/增仓，未贴高、未翻倍、费率未拥挤
    if side == "long_build":
        if chg >= 60 or pos >= 85:
            return None
        if funding >= 0.05:
            return None
        if 3 <= chg < 60 and 12 <= pos <= 78:
            return "拉升埋伏"
        return None
    # 大跌埋伏：空头集中/增仓，未贴地板、未深跌50%
    if side == "short_build":
        if chg <= -50 or pos <= 8:
            return None
        if funding <= -0.05:
            return None
        if chg < 3 and 15 <= pos <= 85:
            return "大跌埋伏"
        return None
    return None


def main() -> int:
    universe = scan_gate_universe(limit=55)
    events: List[Dict[str, Any]] = []
    by_sym = {t["contract"].replace("_", ""): t for t in universe}

    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(analyze_contract, t, True): t for t in universe}
        for fut in as_completed(futs):
            t = futs[fut]
            try:
                for e in fut.result():
                    events.append((e, t))
            except Exception:  # noqa: BLE001
                continue

    long_rows: List[Dict[str, Any]] = []
    short_rows: List[Dict[str, Any]] = []
    seen = set()
    for e, t in events:
        key = (e["symbol"], e.get("side_bias"), e.get("event_type"))
        if key in seen:
            continue
        seen.add(key)
        label = classify(e, t)
        if not label:
            continue
        row = event_row(e, t, label)
        if label == "拉升埋伏":
            long_rows.append(row)
        else:
            short_rows.append(row)

    long_rows.sort(key=lambda x: float(x.get("rescan_priority") or 0), reverse=True)
    short_rows.sort(key=lambda x: float(x.get("rescan_priority") or 0), reverse=True)

    out = {
        "ts": utc_now(),
        "universe": len(universe),
        "emitted": len(long_rows) + len(short_rows),
        "min_quote_vol": MIN_QUOTE_VOL,
        "拉升埋伏": long_rows[:8],
        "大跌埋伏": short_rows[:8],
        "note": "埋伏≠开仓；需结构确认+OI同向增仓+非tipH/tipL+闸门F",
    }
    path = os.path.join(os.path.dirname(__file__), "watch_pool", "ambush_latest.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"[wrote] {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
