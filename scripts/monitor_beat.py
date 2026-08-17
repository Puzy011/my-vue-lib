#!/usr/bin/env python3
"""BEAT 条件监控 — 拉 Gate 数据，对照触发清单输出告警状态。"""

import json
import sys
import urllib.request
from datetime import datetime, timezone

BASE = "https://api.gateio.ws/api/v4"
CONTRACT = "BEAT_USDT"

# --- 监控阈值（可按需调整）---
LEVELS = {
    "support_hard": 0.3237,   # 24h 低 / 失效线
    "support_zone": (0.3237, 0.3350),
    "bounce_target_1": 0.3350,
    "bounce_target_2": 0.3470,  # 15m EMA20 近似
    "reversal_confirm": 0.3700,  # 1h EMA20 近似
    "resistance_major": 0.4500,
}

OI_RULES = {
    "strong_pct": 3.0,
    "extreme_pct": 8.0,
}


def fetch(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def oi_window(stats, n=4):
    if len(stats) < n:
        return None
    cur, old = stats[-1], stats[-n]
    oi = (float(cur["open_interest"]) - float(old["open_interest"])) / float(old["open_interest"]) * 100
    px = (float(cur["mark_price"]) - float(old["mark_price"])) / float(old["mark_price"]) * 100
    if px >= 0 and oi >= 0:
        quad = "多增仓"
    elif px >= 0:
        quad = "空平仓"
    elif oi >= 0:
        quad = "空增仓"
    else:
        quad = "多平仓"
    if quad in ("空平仓", "多平仓"):
        strength = "普通"
    elif abs(oi) >= OI_RULES["extreme_pct"]:
        strength = "极强"
    elif abs(oi) >= OI_RULES["strong_pct"]:
        strength = "强"
    else:
        strength = "普通"
    return {"oi": round(oi, 2), "px": round(px, 2), "quad": quad, "strength": strength}


def check_level(price: float, level: float, tol_pct: float = 0.3) -> bool:
    return abs(price - level) / level * 100 <= tol_pct


def main():
    ticker = next(x for x in fetch(f"{BASE}/futures/usdt/tickers") if x["contract"] == CONTRACT)
    price = float(ticker["last"])
    h24, l24 = float(ticker["high_24h"]), float(ticker["low_24h"])
    pos = (price - l24) / (h24 - l24) * 100 if h24 > l24 else 50

    stats_1h = fetch(f"{BASE}/futures/usdt/contract_stats?contract={CONTRACT}&interval=1h&limit=8")
    stats_15m = fetch(f"{BASE}/futures/usdt/contract_stats?contract={CONTRACT}&interval=15m&limit=8")
    w1h = oi_window(stats_1h, 4)
    w15 = oi_window(stats_15m, 4)

    candles_15m = fetch(f"{BASE}/futures/usdt/candlesticks?contract={CONTRACT}&interval=15m&limit=4")
    last3_yang = sum(1 for c in candles_15m[-3:] if float(c["c"]) >= float(c["o"]))

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    triggers = []

    # --- 看跌 / 失效 ---
    if price < LEVELS["support_hard"]:
        triggers.append({"id": "S1", "level": "危险", "msg": f"跌破硬支撑 {LEVELS['support_hard']} → 加速下行风险"})
    if w1h and w1h["quad"] == "空增仓" and w1h["strength"] == "极强":
        triggers.append({"id": "S2", "level": "压制", "msg": f"1h 空增仓极强 (OI {w1h['oi']:+.1f}%) → 反弹高度受限"})
    if w15 and w15["quad"] == "空增仓" and w15["strength"] in ("强", "极强"):
        triggers.append({"id": "S3", "level": "压制", "msg": f"15m 空增仓{w15['strength']} → 短线仍空"})

    # --- 看涨 / 转折 ---
    if w1h and w1h["quad"] in ("空平仓", "多增仓"):
        triggers.append({"id": "L1", "level": "转折", "msg": f"1h OI 转 {w1h['quad']} → 空压减弱，关注反弹"})
    if w1h and w1h["quad"] == "多增仓" and w1h["strength"] in ("强", "极强"):
        triggers.append({"id": "L2", "level": "强信号", "msg": f"1h 多增仓{w1h['strength']} → 涨的前提成立"})
    if price >= LEVELS["bounce_target_1"]:
        triggers.append({"id": "L3", "level": "反弹", "msg": f"站上 {LEVELS['bounce_target_1']} → 死猫反弹确认（小级别）"})
    if price >= LEVELS["bounce_target_2"]:
        triggers.append({"id": "L4", "level": "反弹", "msg": f"站上 {LEVELS['bounce_target_2']} → 15m 级反弹延续"})
    if price >= LEVELS["reversal_confirm"]:
        triggers.append({"id": "L5", "level": "反转", "msg": f"站上 {LEVELS['reversal_confirm']} → 趋势反转候选"})
    if last3_yang >= 2 and w15 and w15["quad"] != "空增仓":
        triggers.append({"id": "L6", "level": "短线", "msg": "15m 连续阳线 + 空增仓消失 → 短线反弹启动"})

    # --- 场景判定 ---
    if w1h and w1h["quad"] == "空增仓" and w1h["strength"] == "极强":
        scenario = "A-压制中"
        eta = "小反弹或需 1–3 天筑底；1h OI 未转前不谈趋势涨"
    elif w1h and w1h["quad"] in ("空平仓", "多增仓"):
        scenario = "B-筑底/反弹"
        eta = "4–24h 内可看反弹；站 0.347 后看 0.37"
    elif price >= LEVELS["reversal_confirm"]:
        scenario = "C-反转候选"
        eta = "3–7 天+ 看 0.45 区域"
    else:
        scenario = "A-压制中"
        eta = "等 1h OI 从空增仓转向"

    report = {
        "ts": ts,
        "symbol": "BEAT",
        "price": price,
        "range_pos_pct": round(pos, 1),
        "chg24_pct": float(ticker["change_percentage"]),
        "oi_1h": w1h,
        "oi_15m": w15,
        "scenario": scenario,
        "eta_note": eta,
        "levels": LEVELS,
        "triggers": triggers,
        "action": build_action(price, w1h, w15, triggers),
    }

    if "--json" in sys.argv:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_human(report)


def build_action(price, w1h, w15, triggers):
    ids = {t["id"] for t in triggers}
    if "S1" in ids:
        return "观望/回避多 — 硬支撑失守"
    if "L2" in ids or ("L1" in ids and price >= LEVELS["bounce_target_1"]):
        return "可小仓试多 — 设止损 0.323；目标 0.347 → 0.370"
    if "L3" in ids or "L6" in ids:
        return "仅短线反弹思路 — 快进快出，目标 0.347，止损 0.323"
    if w1h and w1h["quad"] == "空增仓" and w1h["strength"] == "极强":
        return "不做多 — 等 1h OI 转空平仓/多增仓后再评估"
    return "观望 — 条件未满足"


def print_human(r):
    print(f"=== BEAT 条件监控 === {r['ts']}")
    print(f"现价: {r['price']:.4f} | 24h位置: {r['range_pos_pct']}% | 24h: {r['chg24_pct']:+.2f}%")
    w1h, w15 = r["oi_1h"], r["oi_15m"]
    if w1h:
        print(f"1h OI: {w1h['quad']} {w1h['strength']} (OI {w1h['oi']:+.2f}%, 价 {w1h['px']:+.2f}%)")
    if w15:
        print(f"15m OI: {w15['quad']} {w15['strength']} (OI {w15['oi']:+.2f}%, 价 {w15['px']:+.2f}%)")
    print(f"场景: {r['scenario']} | {r['eta_note']}")
    print(f"建议: {r['action']}")
    print("\n--- 触发清单 ---")
    for t in r["triggers"]:
        print(f"  [{t['level']}] {t['id']}: {t['msg']}")
    if not r["triggers"]:
        print("  （无新触发，维持观望）")
    print("\n--- 关键价位 ---")
    for k, v in r["levels"].items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
