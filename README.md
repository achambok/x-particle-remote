# X Particle

X-Particle is a super efficient AI forex trading bot powered by LangChain, LangGraph, and MetaTrader 5.

## 🚀 Recent Major Upgrade (January 2026)

The system has been completely overhauled with professional-grade trading features:

### ✅ **New Capabilities:**
- **Real Technical Analysis**: EMA, RSI, MACD, ATR, Bollinger Bands calculations
- **ATR-Based Dynamic Stops**: Stops adapt to market volatility (15-30 pips vs old 2 pips)
- **Proper Position Sizing**: 4% risk calculation (~0.08-0.12 lots vs old 0.02 lots)
- **Trade Validation System**: 15 criteria check before every trade
- **Frequency Controls**: Max 5 trades/day, 60-minute cooldown
- **NO TRADE Decision Support**: Agent outputs NO TRADE when conditions aren't right

### 📊 **Performance Improvements:**
- Trade frequency reduced by 80-95% (1-5/day vs 24/day)
- Proper stop loss sizes (15-30 pips vs 2 pips)
- Correct risk per trade (4% vs 0.4%)
- Spread-aware calculations
- Multi-timeframe confirmation

## 📖 **Documentation**

- **`IMPLEMENTATION_COMPLETE.md`** - Complete summary of all upgrades
- **`UPGRADE_DOCUMENTATION.md`** - Detailed technical specifications
- **`test_upgrade.py`** - Verification script

## 🏃 **Quick Start**

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the bot
python main.py

# Or use PM2 for scheduled runs (every 30 minutes)
pm2 start ecosystem.config.js
```

## 🎯 **What to Expect**

- **~80% of runs:** NO TRADE decision (waiting for quality setup)
- **~20% of runs:** EXECUTE decision with proper parameters
- **Average:** 1-2 trades per day
- **Typical Stop Loss:** 20-25 pips (ATR-based)
- **Position Size:** 0.08-0.12 lots (risk-calculated)

## 🛠️ **Tools & Technologies**

- **MetaTrader 5**: Trading platform
- **LangChain & LangGraph**: AI agent framework
- **Groq API**: LLM provider (gpt-oss-120b model)
- **Tavily API**: Web search for fundamental analysis
- **Pandas & NumPy**: Data analysis and calculations

## 📈 **Key Features**

1. **Technical Analysis**: Real indicator calculations (not hallucinated)
2. **Risk Management**: Dynamic position sizing based on account balance
3. **Trade Validation**: Multi-criteria validation before execution
4. **Frequency Control**: Prevents overtrading with cooldown periods
5. **ATR-Based Stops**: Volatility-adjusted stop loss and take profit
6. **Multi-Timeframe Analysis**: H1, H4, D1 confirmation required

## ⚙️ **Configuration**

Edit `agents/system_prompt.py` to adjust:
- `max_trades_per_day` (default: 5)
- `min_minutes_between_trades` (default: 60)
- Risk percentage (default: 4%)
- Minimum risk-reward ratio (default: 1:3)

## 🔍 **Monitoring**

```python
# Check trade history
import json
with open('logs/trade_history.json') as f:
    print(json.load(f)['daily_stats'])

# Get statistics
from tools import get_trading_statistics_tool
print(get_trading_statistics_tool.invoke({}))
```

## ⚠️ **Important Notes**

- **Most runs should output NO TRADE** - This is correct behavior
- Only trades on high-probability setups
- All trades use proper risk management
- ATR-based stops adapt to market conditions
- System logs all decisions for analysis

## 📝 **Trading Symbols**

EURUSDm, AUDUSDm, GBPUSDm, USDCADm, USDCHFm, USDJPYm, NZDUSDm, XAUUSDm (Gold)

Configure in `.env` file via `SYMBOLS` variable.

## 🎓 **Philosophy**

> "One quality trade is worth more than ten mediocre trades. NO TRADE is better than a bad trade."

The agent is designed to be selective, patient, and disciplined - only trading when all conditions align.

---

**Status:** ✅ Production Ready  
**Last Updated:** January 16, 2026  
**Version:** 2.0 (Major Upgrade)

