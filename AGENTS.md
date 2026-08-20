# Agent 强制规则：合约多空问答

用户发送 `xxxusdt现价做多还是做空`（或等价问法）时：

1. **必须**按 `analysis/beat_framework/RULES.md` 固定 8 步分析。
2. **必须**先跑（或等价拉数）：
   ```bash
   python3 analysis/beat_framework/analyze.py XXXUSDT
   ```
   数据以当时能拉到的交易所为准（Gate/OKX/MEXC；Bybit/Binance 不可用则标 N/A）。
3. **必须**用统一输出：
   ```
   •结论：做多/做空/观望/极强但观望
   •依据：价格；OI强度：x＋方向＋5m/15m/1h/4h；结构；周期；费率
   •执行单：入场 / 止损 / 止盈
   •失效条件：...
   ```
4. 报告模板见 `analysis/beat_framework/REPORT_TEMPLATE.md`（行情/链上/舆情/大额转账/衍生品/CryptoPanic/市场环境）。
5. 推荐硬闸门：
   - 短线空增仓 / EMA空头 → 默认观望，禁止现价多
   - 开多须结构 UP 或突破确认 + OI 仍多增仓
   - OI强/极强只筛选；减仓禁止标极强/强；未过闸门写「极强但观望」
6. 庄币雷达：`analysis/newsliquid/`（`OI_SPIKE` / `OI_CONCENTRATION` / `WHALE_PNL_START`）只进观察池，不自动跟单。JSON Schema 亦见 `src/newsliquid/schemas/`。
