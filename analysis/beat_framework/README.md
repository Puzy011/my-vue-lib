# Beat OI 合约分析框架

本目录固化用户指定的**固定 8 步分析框架**与**统一输出格式**。

## 重要说明

- `main` 分支是 Vue 工程，**不包含实时行情数据**。
- 分析数据一律来自当时可访问的交易所 API（Gate / OKX / MEXC；Bybit/Binance 若被墙则标 N/A）。
- 下次用户只发 `xxxusdt现价做多还是做空` 时，按 `RULES.md` 执行并输出统一四段结论。

## 强制闸门（推荐时）

1. 短线空增仓 / EMA空头 → **默认观望，禁止现价多**
2. 开多必须 **结构UP或突破确认 + OI仍多增仓**
3. OI强/极强 **只筛选**；未过闸门 → **极强但观望**
4. 依据必带：`OI强度：普通/强/极强 ＋ 方向 ＋ 5m/15m/1h/4h`
5. 减仓/去杠杆 **禁止标极强**

庄币雷达见 `../newsliquid/`（事件只进观察池）。

## 文件

| 文件 | 作用 |
|------|------|
| `RULES.md` | 硬规则：OI筛选、闸门F、RANGE禁单边、推荐闸门 |
| `REPORT_TEMPLATE.md` | 固化报告模板 |
| `analyze.py` | 可执行拉数 + 规则引擎 |

## 命令

```bash
# 推荐统一入口
python3 scripts/analyze_contract.py BEATUSDT

python3 analysis/beat_framework/analyze.py BEATUSDT
python3 analysis/beat_framework/analyze.py --scan
python3 analysis/newsliquid/scan_events.py --startup
```

完整规范见 `docs/trading/ANALYSIS_FRAMEWORK.md`。
