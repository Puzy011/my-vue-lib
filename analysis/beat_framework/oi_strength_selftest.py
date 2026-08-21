#!/usr/bin/env python3
"""Offline checks for OI strength / newsliquid helpers (no npm required)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis" / "beat_framework"))
sys.path.insert(0, str(ROOT / "analysis" / "newsliquid"))

from analyze import classify_oi_strength  # noqa: E402
from scan_events import oi_strength_from_chg  # noqa: E402


def assert_eq(got, expect, label: str) -> None:
    if got != expect:
        raise AssertionError(f"{label}: got={got!r} expect={expect!r}")


def main() -> None:
    # Deleveraging never 强/极强
    r = classify_oi_strength(
        {"5m": 0.54, "15m": 0.249, "1h": -1.798, "4h": -9.779},
        {
            "5m": "Q1_涨价增仓",
            "15m": "Q2_跌价增仓",
            "1h": "Q4_跌价减仓",
            "4h": "Q3_涨价减仓",
            "24h": "Q4_跌价减仓",
        },
    )
    assert_eq(r["level"], "普通", "delev level")
    assert_eq(r["deleveraging"], True, "delev flag")

    r = classify_oi_strength(
        {"5m": 2.0, "15m": 6.4, "1h": 12.0, "4h": 41.6},
        {
            "5m": "Q2_跌价增仓",
            "15m": "Q2_跌价增仓",
            "1h": "Q2_跌价增仓",
            "4h": "Q2_跌价增仓",
            "24h": "Q2_跌价增仓",
        },
    )
    assert_eq(r["level"], "极强", "short buildup extreme")

    r = classify_oi_strength(
        {"5m": 5.2, "15m": 2.1, "1h": 1.5, "4h": 2.0},
        {
            "5m": "Q1_涨价增仓",
            "15m": "Q1_涨价增仓",
            "1h": "Q1_涨价增仓",
            "4h": "Q1_涨价增仓",
            "24h": "Q1_涨价增仓",
        },
    )
    assert_eq(r["level"], "极强", "5m extreme threshold")

    assert_eq(oi_strength_from_chg(-12.0, buildup=False), "普通", "neg never extreme")
    assert_eq(oi_strength_from_chg(-12.0, buildup=True), "普通", "neg chg never extreme")
    assert_eq(oi_strength_from_chg(12.0, buildup=True), "极强", "pos extreme")
    assert_eq(oi_strength_from_chg(4.0, buildup=True), "强", "pos strong")
    print("oi_strength_selftest: OK")


if __name__ == "__main__":
    main()
