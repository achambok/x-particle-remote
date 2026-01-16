# Copilot Instructions for x-particle AI Forex Trading Bot

## Project Overview
- **Purpose:** AI-powered, fully automated Forex trading bot using MetaTrader 5, LangChain, and LangGraph.
- **Agent Name:** "Jannat" - The AI trader persona defined in the system prompt.
- **Key Pairs:** Only trades EURUSD, AUDUSD, GBPUSD, USDCAD, USDCHF, USDJPY, NZDUSD, and XAUUSD (Gold). Symbol list configured via `SYMBOLS` env var in `config/environments.py`.
- **Architecture:**
  - `main.py`: Entry point that invokes the agent with a simple message.
  - `agents/`: Main agent logic (`main_agent.py`) and system prompt (`system_prompt.py`).
  - `metatrader/`: All MT5 integration (account info, orders, market data, indicators, trade frequency) via common connection handler.
    - `indicators.py`: Technical indicator calculations (EMA, RSI, MACD, ATR, Bollinger Bands, support/resistance, position sizing).
    - `trade_frequency.py`: Trade frequency tracking and cooldown enforcement.
  - `tools/`: LangChain `@tool` decorators wrapping MT5 operations, technical analysis, and Tavily web search (27 tools total).
    - `technical_analysis_tools.py`: 4 comprehensive analysis and validation tools.
    - `trade_frequency_tools.py`: 3 trade frequency control tools.
    - `dynamic_stops_tools.py`: 2 ATR-based dynamic stop/TP calculation tools.
  - `config/`: Environment variables (`environments.py`), API keys, MT5 credentials.
  - `llm/`: Groq LLM configuration (`groq.py`) - currently using `openai/gpt-oss-120b` model.

## Agent & Workflow Patterns
- **LangGraph State Machine:** 
  - `START` → `llm_call` → conditional edge to `tool_node` or `END`
  - `tool_node` → back to `llm_call` (loop until no more tool calls)
  - State tracked in `MessagesState` with message history and `llm_calls` counter.
- **System Prompt:** Comprehensive 450-line prompt defining 5-phase mandatory workflow, 15 NO TRADE criteria, risk rules (4% per trade, 8-10% total), and "NO TRADE is better than bad trade" philosophy. See `agents/system_prompt.py`.
- **Tool Registration:** All tools listed in `agents/main_agent.py` and bound to the model via `.bind_tools(tools)`.
- **Order Execution:** Use `OrderRequest` dataclass and `send_order()` in `metatrader/metatrader.py`. All MT5 functions return `{"success": bool, "error": str}` dicts.

## Key Conventions & Patterns
- **MT5 Connection:** All operations call `ensure_mt5_connection()` from `metatrader/common.py` before interacting with MT5.
- **Order Types:** Mapped via `order_type_map` dict: "BUY", "SELL", "BUY_LIMIT", "SELL_LIMIT", "BUY_STOP", "SELL_STOP".
- **Risk Management (upgraded system):**
  - 4% risk per trade (dynamic calculation), 8-10% total concurrent risk.
  - Volume calculated dynamically via `calculate_position_size()` using balance, risk%, SL distance, pip value.
  - ATR-based dynamic stops (15-30 pips typical) replace fixed stops.
  - Spread-aware TP/SL calculation via `calculate_atr_based_stops_tool`.
  - Minimum 1:3 risk-reward ratio enforced.
  - Trade frequency limits: Max 5 trades/day, 60-minute cooldown between trades.
  - Position sizing typically 0.08-0.12 lots (for $500 balance) vs old 0.02 hardcoded.
- **Data Flow (5-Phase Mandatory Workflow):**
  1. **Health Check:** Verify account status, check trade frequency limits, review open positions.
  2. **Technical Analysis:** Calculate real indicators via `calculate_technical_indicators_tool` (EMA, RSI, MACD, ATR, Bollinger, support/resistance).
  3. **Fundamental Analysis:** Research market sentiment via Tavily web search.
  4. **Validation:** Run `validate_trade_setup_tool` with 5 critical checks (trend alignment, indicator confluence, risk/reward, volatility, correlation).
  5. **Decision:** Either NO TRADE (70-90% of cases) or EXECUTE with parameters from `recommend_trade_parameters_tool`.
  - Agent must justify against 15 NO TRADE criteria before executing.
  - All executions use `send_order_tool` with ATR-based stops and dynamic position sizing.
- **Error Handling:** All MT5 operations return structured dicts with `success` and `error` fields. Always check these before proceeding.

## Developer Workflows
- **Run:** `python main.py` (logs to `agent.log` via Python `logging` module).
- **Environment:** Requires `.env` file with `GROQ_API_KEY`, `TAVILY_API_KEY`, MT5 credentials (`LOGIN`, `PASSWD`, `SERVER`), `SYMBOLS`, `MAGIC_NUMBER`, `OFF_DAYS`.
- **Dependencies:** Install via `pip install -r requirements.txt` (MetaTrader5, LangChain, LangGraph, Groq, Tavily, pandas).
- **Debugging:** Check `agent.log` for agent decisions. Check `logs/trade_history.json` for trade frequency tracking. MT5 errors are in returned dicts. Use `mt5.last_error()` if connection fails. See `UPGRADE_DOCUMENTATION.md` for system architecture and `IMPLEMENTATION_COMPLETE.md` for upgrade summary.
- **Extending Tools:**
  1. Create new tool function with `@tool` decorator in appropriate `tools/*.py` file:
     - `account_tools.py`: Account info and balance queries.
     - `orders_tools.py`: Order execution and position management.
     - `market_data_tools.py`: Candle data and price queries.
     - `technical_analysis_tools.py`: Indicator calculations and validation.
     - `dynamic_stops_tools.py`: ATR-based risk parameters.
     - `trade_frequency_tools.py`: Frequency tracking and cooldown.
  2. If adding calculations, consider adding to `metatrader/indicators.py` for reusability.
  3. Import and add to `tools` list in `agents/main_agent.py` (currently 27 tools).
  4. Update system prompt in `agents/system_prompt.py` to describe usage in 5-phase workflow.

## Integration Points
- **MetaTrader 5:** Windows-only library. Requires MT5 terminal installed and logged in.
- **Groq API:** LLM provider via `langchain_groq.ChatGroq`. Configured in `llm/groq.py`.
- **Tavily API:** Web search for fundamental analysis via `tavily_web_search_tool`.
- **LangChain/LangGraph:** Core agent framework. Tools automatically serialized for LLM function calling.

## Key Features & Improvements
- **Technical Indicators:** Real calculations (not hallucinated) via `metatrader/indicators.py`:
  - `calculate_ema(data, period)`, `calculate_rsi(data, 14)`, `calculate_macd(data)`
  - `calculate_atr(data, 14)`, `calculate_bollinger_bands(data, 20)`
  - `calculate_support_resistance(data)`, `calculate_position_size(balance, risk%, sl_pips, symbol)`
- **Trade Validation:** 5-check system via `validate_trade_setup_tool`:
  - Trend alignment (EMA 20/50/200), Indicator confluence (3+ bullish/bearish signals)
  - Risk/reward ratio (minimum 1:3), Volatility check (ATR-based), Correlation awareness
- **Frequency Controls:** Max 5 trades/day, 60-minute cooldown via `trade_frequency.py`
- **Dynamic Stops:** ATR-based SL/TP calculation (2.0x ATR for SL, 6.0x for TP) with spread adjustment
- **Position Sizing:** Dynamic calculation based on 4% account risk, SL distance, and pip value
- **NO TRADE Support:** System prompt enforces 15 rejection criteria, expects 70-90% NO TRADE rate
- **Performance Metrics:** Win rate requirement reduced from 92% (impossible) to 28% (achievable)

## Examples
- **Get trade recommendations:** Call `recommend_trade_parameters_tool` with symbol and direction - returns complete setup with ATR-based stops, position size, and spread-adjusted TP/SL.
- **Calculate indicators:** Call `calculate_technical_indicators_tool` with symbol and timeframe - returns EMA, RSI, MACD, ATR, Bollinger Bands, support/resistance.
- **Validate setup:** Call `validate_trade_setup_tool` with symbol, direction, and indicators - runs 5 critical checks and returns pass/fail with reasons.
- **Check frequency:** Call `check_trade_frequency_tool` - returns `can_trade` boolean and reason (cooldown, daily limit, etc.).
- **Place a trade:** Call `send_order_tool` with symbol, volume, order_type, sl_points, tp_points (get these from `recommend_trade_parameters_tool`).
- **Add a tool:** See `tools/technical_analysis_tools.py` for reference pattern using `@tool` decorator and MT5 wrapper functions.
- **Change LLM model:** Edit `llm/groq.py` `model` parameter (e.g., to `"claude-3-5-haiku-20241022"` if switching providers).

---
For agent behavior details, see `agents/system_prompt.py` (450-line comprehensive workflow).
For symbol whitelist and risk rules, check `config/environments.py`.
For upgrade documentation, see `UPGRADE_DOCUMENTATION.md` and `IMPLEMENTATION_COMPLETE.md`.
For testing, run `python test_upgrade.py` (verifies all 27 tools) or `python test_position_sizing.py` (demonstrates dynamic sizing).
