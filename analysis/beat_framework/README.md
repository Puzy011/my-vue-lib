# Beat OI 合约分析框架

本目录固化用户指定的**固定 8 步分析框架**与**统一输出格式**。

## 重要说明

- `main` 分支是 Vue 工程，**不包含实时行情数据**。
- 分析数据一律来自当时可访问的交易所 API（Gate / OKX / MEXC；Bybit/Binance 若被墙则标 N/A）。
- 下次用户只发 `xxxusdt现价做多还是做空` 时，按 `RULES.md` 执行并输出统一四段结论。

## 文件

| 文件 | 作用 |
|------|------|
| `RULES.md` | 硬规则：OI筛选、闸门F、RANGE禁单边 |
| `REPORT_TEMPLATE.md` | 固化报告模板（行情/链上/舆情/转账/OI费率/新闻/环境） |
| `analyze.py` | 可执行拉数 + 规则引擎 |

## 命令

```bash
# 单币完整报告
python3 analysis/beat_framework/analyze.py BEATUSDT

# JSON
python3 analysis/beat_framework/analyze.py ETHUSDT --json

# OI 强单边扫描（RANGE/F 闸门后）
python3 analysis/beat_framework/analyze.py --scan
```

报告写入 `analysis/reports/`。
