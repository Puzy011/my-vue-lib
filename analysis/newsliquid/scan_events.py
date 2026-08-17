#!/usr/bin/env python3
"""newsliquid MVP scanner: OI_SPIKE + OI_CONCENTRATION → observe pool only.

Never auto-opens trades. WHALE_PNL_START is emitted as blocked without a paid source.

启动期强庄雷达 (--startup): 捕捉正在启动的多头增仓币，按 OI 加速排序并优先重扫。
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
COOLDOWN_MIN_SEC = 180
OI_ACCEL_RESCAN_MIN = 1.5
DEFAULT_COOLDOWN_STATE = "analysis/newsliquid/watch_pool/cooldown.json"
DEFAULT_PRIORITY_STATE = "analysis/newsliquid/watch_pool/priority_rescan.json"


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


def load_priority_rescan(path: str) -> List[Dict[str, Any]]:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        rows = data.get("symbols") or []
        return sorted(rows, key=lambda x: float(x.get("rescan_priority") or 0), reverse=True)
    except Exception:  # noqa: BLE001
        return []


def save_priority_rescan(path: str, symbols: List[Dict[str, Any]]) -> None:
    import os

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "ts_utc": utc_now(),
                "note": "OI加速优先重扫队列；下次 --startup 会优先纳入扫描",
                "symbols": symbols,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def in_cooldown(state: Dict[str, float], key: str, cooldown: int = COOLDOWN_SEC) -> bool:
    last = state.get(key)
    if last is None:
        return False
    return (time.time() - last) < cooldown


def pct(a: float, b: float) -> Optional[float]:
    if b == 0:
        return None
    return (a / b - 1.0) * 100.0


def cooldown_for_accel(oi_accel: float) -> int:
    """OI 加速越高 → 冷却越短，便于优先重扫。"""
    if oi_accel >= 5.0:
        return COOLDOWN_MIN_SEC
    if oi_accel >= 3.0:
        return 300
    if oi_accel >= OI_ACCEL_RESCAN_MIN:
        return 600
    return COOLDOWN_SEC


def rescan_priority_score(oi_accel: float, oi_chg: float, chg24: float, side: str) -> float:
    score = oi_accel * 2.0 + max(oi_chg, 0.0) * 0.25
    if side == "long_build" and 3 <= chg24 < 60:
        score += 2.0
    return round(score, 3)


def compute_oi_accel_profile(ordered: List[dict]) -> Dict[str, float]:
    """基于 ~5m contract_stats 计算 OI 变化与加速（百分点差）。"""
    if len(ordered) < 3:
        return {}
    oi = [float(x["open_interest"]) for x in ordered]
    chg_now = pct(oi[-1], oi[-2])
    chg_prev = pct(oi[-2], oi[-3])
    if chg_now is None:
        chg_now = 0.0
    if chg_prev is None:
        chg_prev = 0.0
    profile: Dict[str, float] = {
        "oi_chg_5m": round(chg_now, 3),
        "oi_chg_prev_5m": round(chg_prev, 3),
        "oi_accel_5m": round(chg_now - chg_prev, 3),
    }
    if len(oi) >= 7:
        chg_15m = pct(oi[-1], oi[-4])
        chg_15m_prev = pct(oi[-4], oi[-7])
        if chg_15m is not None and chg_15m_prev is not None:
            profile["oi_chg_15m"] = round(chg_15m, 3)
            profile["oi_accel_15m"] = round(chg_15m - chg_15m_prev, 3)
    return profile


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
    cooldown_sec: int = COOLDOWN_SEC,
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
        "cooldown_sec": cooldown_sec,
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


def scan_gate_universe(limit: int = 40, extra_symbols: Optional[List[str]] = None) -> List[dict]:
    data, err = safe_get("https://api.gateio.ws/api/v4/futures/usdt/tickers")
    if err or not data:
        return []
    by_contract: Dict[str, dict] = {}
    rows: List[Tuple[float, dict]] = []
    for t in data:
        try:
            contract = t["contract"]
            by_contract[contract] = t
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
    picked: List[dict] = [t for _, t in rows[:limit]]
    seen = {t["contract"] for t in picked}

    if extra_symbols:
        for sym in extra_symbols:
            contract = sym.replace("USDT", "_USDT")
            if contract in seen:
                continue
            t = by_contract.get(contract)
            if t is None:
                continue
            picked.append(t)
            seen.add(contract)

    return picked


def analyze_contract(ticker: dict, oi_accel_priority: bool = False) -> List[Dict[str, Any]]:
    contract = ticker["contract"]
    symbol = contract.replace("_", "")
    last = float(ticker["last"])
    chg24 = float(ticker.get("change_percentage") or 0)
    high = float(ticker["high_24h"])
    low = float(ticker["low_24h"])
    funding = float(ticker.get("funding_rate") or ticker.get("funding_rate_indicative") or 0) * 100
    pos = ((last - low) / (high - low) * 100) if high > low else None

    events: List[Dict[str, Any]] = []

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
    accel_profile = compute_oi_accel_profile(ordered)
    oi_accel_5m = accel_profile.get("oi_accel_5m", 0.0)

    spike_candidates: List[Tuple[float, str, str, float, float, str]] = []
    windows = [("5m", 1, OI_SPIKE_5M), ("15m", 3, OI_SPIKE_15M), ("1h", 12, OI_SPIKE_1H)]
    for tf, n, thr in windows:
        if len(ordered) <= n:
            continue
        oi_prev = float(ordered[-1 - n]["open_interest"])
        oi_chg = pct(oi_now, oi_prev)
        if oi_chg is None or oi_chg <= 0:
            continue
        if oi_chg < thr:
            continue
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

        if tf == "5m":
            window_accel = oi_accel_5m
        elif tf == "15m":
            window_accel = accel_profile.get("oi_accel_15m", oi_accel_5m)
        else:
            window_accel = oi_accel_5m * 0.5
        spike_candidates.append((window_accel, tf, side, oi_chg, px_chg, quad))

    if spike_candidates:
        if oi_accel_priority:
            spike_candidates.sort(key=lambda x: x[0], reverse=True)
        else:
            spike_candidates.sort(key=lambda x: (x[1] != "5m", x[1] != "15m", -x[3]))

        _, tf, side, oi_chg, px_chg, quad = spike_candidates[0]
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

        cd = cooldown_for_accel(oi_accel_5m)
        priority = rescan_priority_score(oi_accel_5m, oi_chg, chg24, side)
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
                    **accel_profile,
                },
                {"oi_chg_5m_pct": OI_SPIKE_5M, "oi_chg_15m_pct": OI_SPIKE_15M, "oi_chg_1h_pct": OI_SPIKE_1H},
                {
                    "oi_strength": oi_strength_from_chg(oi_chg),
                    "oi_accel_5m": oi_accel_5m,
                    "rescan_priority": priority,
                    "range_suspected": abs(chg24) < 2,
                    "funding_pct": round(funding, 4),
                    "chg24_pct": round(chg24, 2),
                    "tip_chase_risk": tip_risk,
                    "note": "OI极强≠开仓许可；需结构确认+OI仍同向增仓",
                },
                severity=severity,
                severity_reason=reason,
                tf=tf,
                cooldown_sec=cd,
            )
        )

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
                cd = cooldown_for_accel(oi_accel_5m)
                priority = rescan_priority_score(oi_accel_5m, conc * 0.1, chg24, side)
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
                            **accel_profile,
                        },
                        {"concentration_pct": CONCENTRATION_PCT},
                        {
                            "oi_strength": "强" if conc >= 60 else "普通",
                            "oi_accel_5m": oi_accel_5m,
                            "rescan_priority": priority,
                            "range_suspected": abs(chg24) < 2,
                            "funding_pct": round(funding, 4),
                            "chg24_pct": round(chg24, 2),
                            "tip_chase_risk": abs(chg24) >= 50,
                            "note": "集中度是主力代理，不是开仓许可",
                        },
                        severity=sev,
                        severity_reason=reason,
                        tf="1h",
                        cooldown_sec=cd,
                    )
                )

    return events


def whale_pnl_placeholder(symbols: List[str]) -> List[Dict[str, Any]]:
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
                {
                    "oi_strength": "普通",
                    "range_suspected": False,
                    "funding_pct": None,
                    "chg24_pct": None,
                    "tip_chase_risk": False,
                    "note": "无PnL源",
                },
                severity="blocked",
                severity_reason="无付费聪明钱/PnL源，禁止假装主力已启动",
                tf="na",
            )
        )
    return out


def annotate_startup_phase(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    startup: List[Dict[str, Any]] = []
    for e in events:
        chg = (e.get("gates_hint") or {}).get("chg24_pct")
        tip = (e.get("gates_hint") or {}).get("tip_chase_risk")
        side = e.get("side_bias")
        oi_accel = (e.get("gates_hint") or {}).get("oi_accel_5m", 0)
        if e.get("severity") == "blocked":
            continue
        if tip or (chg is not None and chg >= 100):
            e["startup_phase"] = "降级-禁止追开"
        elif side == "long_build" and chg is not None and 3 <= chg < 60:
            if oi_accel >= OI_ACCEL_RESCAN_MIN:
                e["startup_phase"] = "早期/加速观察"
            else:
                e["startup_phase"] = "早期/待加速确认"
            startup.append(e)
        else:
            e["startup_phase"] = "非启动多头"
    startup.sort(
        key=lambda x: float((x.get("gates_hint") or {}).get("rescan_priority") or 0),
        reverse=True,
    )
    return startup


def build_priority_queue(startup: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    queue: List[Dict[str, Any]] = []
    for e in startup:
        accel = float((e.get("gates_hint") or {}).get("oi_accel_5m") or 0)
        if accel < OI_ACCEL_RESCAN_MIN:
            continue
        queue.append(
            {
                "symbol": e["symbol"],
                "oi_accel_5m": accel,
                "rescan_priority": (e.get("gates_hint") or {}).get("rescan_priority"),
                "cooldown_sec": e.get("cooldown_sec", COOLDOWN_SEC),
                "startup_phase": e.get("startup_phase"),
            }
        )
    queue.sort(key=lambda x: float(x.get("rescan_priority") or 0), reverse=True)
    return queue


def run_once(
    out_path: str,
    cooldown_path: str,
    with_whale_stub: bool = False,
    startup_mode: bool = False,
    priority_path: str = DEFAULT_PRIORITY_STATE,
) -> Dict[str, Any]:
    priority_rows = load_priority_rescan(priority_path) if startup_mode else []
    extra_symbols = [r["symbol"] for r in priority_rows]
    universe = scan_gate_universe(extra_symbols=extra_symbols if startup_mode else None)
    cooldown = load_cooldown(cooldown_path)
    events: List[Dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(analyze_contract, t, startup_mode) for t in universe]
        for fut in as_completed(futs):
            try:
                events.extend(fut.result())
            except Exception:  # noqa: BLE001
                continue

    # OI 加速优先：高优先级事件先过冷却闸门
    events.sort(
        key=lambda ev: float((ev.get("gates_hint") or {}).get("rescan_priority") or 0),
        reverse=True,
    )

    accepted: List[Dict[str, Any]] = []
    seen = set()
    for ev in events:
        dk = ev["dedupe_key"]
        if dk in seen:
            continue
        seen.add(dk)
        cd = int(ev.get("cooldown_sec") or COOLDOWN_SEC)
        if in_cooldown(cooldown, dk, cd):
            continue
        accepted.append(ev)
        cooldown[dk] = time.time()

    if with_whale_stub and accepted:
        accepted.extend(whale_pnl_placeholder([e["symbol"] for e in accepted]))

    save_cooldown(cooldown_path, cooldown)

    result: Dict[str, Any] = {
        "ts_utc": utc_now(),
        "universe": len(universe),
        "emitted": len(accepted),
        "pool": "observe",
        "note": "事件只进观察池；开仓仍过结构/背离/闸门F/tipH·tipL",
        "events": accepted,
    }

    if startup_mode:
        startup = annotate_startup_phase(accepted)
        result["startup_long_watch"] = startup
        result["mode"] = "startup"
        result["priority_rescan"] = build_priority_queue(startup)
        save_priority_rescan(priority_path, result["priority_rescan"])

    import os

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def main() -> int:
    p = argparse.ArgumentParser(description="newsliquid observe-pool scanner")
    p.add_argument("--once", action="store_true", default=True)
    p.add_argument(
        "--startup",
        action="store_true",
        help="启动期强庄雷达：OI加速优先选窗+优先重扫+未翻倍+非tipH",
    )
    p.add_argument("--out", default="analysis/newsliquid/watch_pool/latest.json")
    p.add_argument("--cooldown", default=DEFAULT_COOLDOWN_STATE)
    p.add_argument("--priority", default=DEFAULT_PRIORITY_STATE, help="OI加速优先重扫队列落盘")
    p.add_argument("--whale-stub", action="store_true", help="Emit blocked WHALE_PNL_START stubs")
    p.add_argument("--ignore-cooldown", action="store_true", help="清空冷却，强制全量重扫")
    args = p.parse_args()

    if args.startup:
        if args.out == "analysis/newsliquid/watch_pool/latest.json":
            args.out = "analysis/newsliquid/watch_pool/startup_latest.json"
        if args.ignore_cooldown:
            open(args.cooldown, "w").write("{}")

        result = run_once(
            args.out,
            args.cooldown,
            with_whale_stub=False,
            startup_mode=True,
            priority_path=args.priority,
        )
        startup = result.get("startup_long_watch") or []
        print(
            json.dumps(
                {
                    "ts": result["ts_utc"],
                    "mode": "startup",
                    "startup_long_watch": [
                        {
                            "symbol": e["symbol"],
                            "type": e["event_type"],
                            "severity": e["severity"],
                            "startup_phase": e.get("startup_phase"),
                            "oi_strength": e.get("gates_hint", {}).get("oi_strength"),
                            "oi_accel_5m": e.get("gates_hint", {}).get("oi_accel_5m"),
                            "rescan_priority": e.get("gates_hint", {}).get("rescan_priority"),
                            "cooldown_sec": e.get("cooldown_sec"),
                            "chg24": e.get("gates_hint", {}).get("chg24_pct"),
                            "payload": e.get("payload"),
                            "reason": e.get("severity_reason"),
                        }
                        for e in startup
                    ],
                    "priority_rescan": result.get("priority_rescan"),
                    "all_events": len(result.get("events") or []),
                    "note": "启动雷达≠开仓；OI加速高者优先重扫；需结构UP+OI仍多增仓+非tipH+闸门F",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        print(f"[wrote] {args.out}")
        print(f"[wrote] {args.priority}")
        return 0

    result = run_once(args.out, args.cooldown, with_whale_stub=args.whale_stub)
    summary = [
        {
            "type": e["event_type"],
            "symbol": e["symbol"],
            "severity": e["severity"],
            "side": e["side_bias"],
            "reason": e["severity_reason"],
            "oi_strength": e.get("gates_hint", {}).get("oi_strength"),
            "oi_accel_5m": e.get("gates_hint", {}).get("oi_accel_5m"),
            "rescan_priority": e.get("gates_hint", {}).get("rescan_priority"),
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
