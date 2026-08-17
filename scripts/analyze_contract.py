#!/usr/bin/env python3
"""统一入口：xxxUSDT 固定框架分析。

触发：用户发「xxxusdt现价做多还是做空」→ 运行本脚本。

规范：docs/trading/ANALYSIS_FRAMEWORK.md
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYZE = os.path.join(ROOT, "analysis", "beat_framework", "analyze.py")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="固定8步框架：现价/OI/结构/周期/费率/事件/结论/执行"
    )
    parser.add_argument("symbol", nargs="?", default="BTCUSDT", help="例如 BTCUSDT 或 btc")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--scan", action="store_true", help="OI 强单边候选扫描")
    parser.add_argument("--out", default="", help="报告落盘路径")
    parser.add_argument(
        "--startup-scan",
        action="store_true",
        help="额外运行 newsliquid 启动期强庄雷达",
    )
    args = parser.parse_args()

    cmd = [sys.executable, ANALYZE, args.symbol]
    if args.json:
        cmd.append("--json")
    if args.scan:
        cmd = [sys.executable, ANALYZE, "--scan"]
    if args.out:
        cmd.extend(["--out", args.out])

    rc = subprocess.call(cmd, cwd=ROOT)
    if rc != 0:
        return rc

    if args.startup_scan and not args.scan:
        scan = os.path.join(ROOT, "analysis", "newsliquid", "scan_events.py")
        subprocess.call([sys.executable, scan, "--startup"], cwd=ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
