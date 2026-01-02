# Copilot Instructions for x-particle AI Forex Trading Bot

## Project Overview
- **Purpose:** AI-powered, fully automated Forex trading bot using MetaTrader 5, LangChain, and LangGraph.
- **Agent Name:** "Jannat" - The AI trader persona defined in the system prompt.
- **Key Pairs:** Only trades EURUSD, AUDUSD, GBPUSD, USDCAD, USDCHF, USDJPY, NZDUSD, and XAUUSD (Gold). Symbol list configured via `SYMBOLS` env var in `config/environments.py`.
- **Architecture:**
  - `main.py`: Entry point that invokes the agent with a simple message.
  - `agents/`: Main agent logic (`main_agent.py`) and system prompt (`system_prompt.py`).
  - `metatrader/`: All MT5 integration (account info, orders, market data) via common connection handler.
  - `tools/`: LangChain `@tool` decorators wrapping MT5 operations and Tavily web search.
  - `config/`: Environment variables (`environments.py`), API keys, MT5 credentials.
  - `llm/`: Groq LLM configuration (`groq.py`) - currently using `openai/gpt-oss-120b` model.

## Agent & Workflow Patterns
- **LangGraph State Machine:** 
  - `START` → `llm_call` → conditional edge to `tool_node` or `END`
  - `tool_node` → back to `llm_call` (loop until no more tool calls)
  - State tracked in `MessagesState` with message history and `llm_calls` counter.
- **System Prompt:** Defines risk rules (4-5% per trade, 8-10% total), 10-step workflow, and trading strategies. See `agents/system_prompt.py`.
- **Tool Registration:** All tools listed in `agents/main_agent.py` and bound to the model via `.bind_tools(tools)`.
- **Order Execution:** Use `OrderRequest` dataclass and `send_order()` in `metatrader/metatrader.py`. All MT5 functions return `{"success": bool, "error": str}` dicts.

## Key Conventions & Patterns
- **MT5 Connection:** All operations call `ensure_mt5_connection()` from `metatrader/common.py` before interacting with MT5.
- **Order Types:** Mapped via `order_type_map` dict: "BUY", "SELL", "BUY_LIMIT", "SELL_LIMIT", "BUY_STOP", "SELL_STOP".
- **Risk Management (from system prompt):**
  - 4-5% risk per trade, 8-10% total concurrent risk.
  - Volume calculated dynamically from balance, stop-loss distance, pip value, leverage.
  - Minimum 1:3 risk-reward ratio enforced.
- **Data Flow:**
  1. Agent calls tools to gather account info, positions, history, candle data.
  2. Performs technical (EMAs, RSI, MACD, Bollinger Bands, ATR) and fundamental analysis (Tavily search).
  3. Generates trade plan if high-probability setup exists.
  4. Executes via `send_order_tool`.
- **Error Handling:** All MT5 operations return structured dicts with `success` and `error` fields. Always check these before proceeding.

## Developer Workflows
- **Run:** `python main.py` (logs to `agent.log` via Python `logging` module).
- **Environment:** Requires `.env` file with `GROQ_API_KEY`, `TAVILY_API_KEY`, MT5 credentials (`LOGIN`, `PASSWD`, `SERVER`), `SYMBOLS`, `MAGIC_NUMBER`, `OFF_DAYS`.
- **Dependencies:** Install via `pip install -r requirements.txt` (MetaTrader5, LangChain, LangGraph, Groq, Tavily, pandas).
- **Debugging:** Check `agent.log` for agent decisions. MT5 errors are in returned dicts. Use `mt5.last_error()` if connection fails.
- **Extending Tools:**
  1. Create new tool function with `@tool` decorator in appropriate `tools/*.py` file.
  2. Import and add to `tools` list in `agents/main_agent.py`.
  3. If needed, update system prompt in `agents/system_prompt.py` to describe usage.

## Integration Points
- **MetaTrader 5:** Windows-only library. Requires MT5 terminal installed and logged in.
- **Groq API:** LLM provider via `langchain_groq.ChatGroq`. Configured in `llm/groq.py`.
- **Tavily API:** Web search for fundamental analysis via `tavily_web_search_tool`.
- **LangChain/LangGraph:** Core agent framework. Tools automatically serialized for LLM function calling.

## Examples
- **Place a trade:** Call `send_order_tool` with symbol, volume, order_type, sl_points, tp_points.
- **Add a tool:** See `tools/account_tools.py` for reference pattern using `@tool` decorator and MT5 wrapper functions.
- **Change LLM model:** Edit `llm/groq.py` `model` parameter (e.g., to `"claude-3-5-haiku-20241022"` if switching providers).

---
For agent behavior details, see `agents/system_prompt.py`. For symbol whitelist and risk rules, check `config/environments.py`.
