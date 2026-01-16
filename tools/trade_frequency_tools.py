from metatrader.trade_frequency import (
    can_trade_now,
    log_trade_attempt,
    get_trading_stats,
    get_trades_today
)
from langchain.tools import tool
import json


@tool
def check_trade_frequency_tool(
    max_trades_per_day: int = 5,
    min_minutes_between_trades: int = 60
) -> dict:
    """
    Check if trading is allowed based on frequency and cooldown rules.
    
    THIS MUST BE CALLED BEFORE EVERY TRADE ATTEMPT.
    
    Args:
        max_trades_per_day (int): Maximum trades allowed per day (default 5)
        min_minutes_between_trades (int): Minimum minutes between trades (default 60)
        
    Returns:
        dict: Trading frequency status including:
            - allowed (bool): Whether trading is allowed
            - reason (str): Explanation
            - trades_today (int): Number of trades executed today
            - minutes_since_last_trade (float): Time since last trade
            - cooldown_remaining (float): Minutes until next trade allowed
    """
    result = can_trade_now(max_trades_per_day, min_minutes_between_trades)
    
    # Add cooldown remaining info
    if not result['allowed'] and result['minutes_since_last_trade'] is not None:
        result['cooldown_remaining'] = min_minutes_between_trades - result['minutes_since_last_trade']
    else:
        result['cooldown_remaining'] = 0
    
    return json.dumps(result, default=str)


@tool
def get_trading_statistics_tool() -> dict:
    """
    Get comprehensive trading statistics for the last 7 days.
    
    Returns:
        dict: Trading statistics including:
            - total_attempts: Total trade attempts
            - successful_trades: Trades that were executed
            - rejected_trades: Trades that were rejected by validation
            - rejection_rate_pct: Percentage of trades rejected
            - avg_trades_per_day: Average successful trades per day
            - today: Today's statistics
    """
    stats = get_trading_stats()
    return json.dumps(stats, default=str)


@tool
def log_trade_decision_tool(
    symbol: str,
    order_type: str,
    volume: float,
    decision: str,
    reason: str
) -> dict:
    """
    Log a trading decision (executed or rejected) for tracking and analysis.
    
    Args:
        symbol (str): Trading symbol
        order_type (str): 'BUY' or 'SELL'
        volume (float): Position size
        decision (str): 'EXECUTED' or 'REJECTED'
        reason (str): Reason for the decision
        
    Returns:
        dict: Confirmation of logged decision
    """
    success = decision == 'EXECUTED'
    log_trade_attempt(symbol, order_type, volume, success, reason)
    
    return json.dumps({
        "logged": True,
        "symbol": symbol,
        "decision": decision,
        "reason": reason,
        "trades_today_after_logging": get_trades_today()
    }, default=str)
