import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional


TRADE_LOG_FILE = "logs/trade_history.json"


def ensure_trade_log_exists():
    """Ensure the trade log file exists"""
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, 'w') as f:
            json.dump({"trades": [], "daily_stats": {}}, f)


def load_trade_log() -> Dict:
    """Load trade history from file"""
    ensure_trade_log_exists()
    try:
        with open(TRADE_LOG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"trades": [], "daily_stats": {}}


def save_trade_log(data: Dict):
    """Save trade history to file"""
    ensure_trade_log_exists()
    with open(TRADE_LOG_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def log_trade_attempt(symbol: str, order_type: str, volume: float, success: bool, reason: str = ""):
    """Log a trade attempt (successful or rejected)"""
    log_data = load_trade_log()
    
    trade_entry = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "order_type": order_type,
        "volume": volume,
        "success": success,
        "reason": reason
    }
    
    log_data["trades"].append(trade_entry)
    
    # Update daily stats
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in log_data["daily_stats"]:
        log_data["daily_stats"][today] = {
            "total_attempts": 0,
            "successful_trades": 0,
            "rejected_trades": 0,
            "last_trade_time": None
        }
    
    log_data["daily_stats"][today]["total_attempts"] += 1
    if success:
        log_data["daily_stats"][today]["successful_trades"] += 1
    else:
        log_data["daily_stats"][today]["rejected_trades"] += 1
    log_data["daily_stats"][today]["last_trade_time"] = trade_entry["timestamp"]
    
    save_trade_log(log_data)


def get_trades_today() -> int:
    """Get number of trades executed today"""
    log_data = load_trade_log()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if today in log_data["daily_stats"]:
        return log_data["daily_stats"][today]["successful_trades"]
    return 0


def get_last_trade_time() -> Optional[datetime]:
    """Get timestamp of last trade"""
    log_data = load_trade_log()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if today in log_data["daily_stats"]:
        last_time_str = log_data["daily_stats"][today].get("last_trade_time")
        if last_time_str:
            return datetime.fromisoformat(last_time_str)
    return None


def can_trade_now(max_trades_per_day: int = 5, min_minutes_between_trades: int = 60) -> Dict:
    """
    Check if trading is allowed based on frequency rules.
    
    Args:
        max_trades_per_day: Maximum trades allowed per day
        min_minutes_between_trades: Minimum cooldown period between trades
        
    Returns:
        dict: {
            "allowed": bool,
            "reason": str,
            "trades_today": int,
            "minutes_since_last_trade": float
        }
    """
    trades_today = get_trades_today()
    last_trade_time = get_last_trade_time()
    
    # Check daily limit
    if trades_today >= max_trades_per_day:
        return {
            "allowed": False,
            "reason": f"Daily trade limit reached: {trades_today}/{max_trades_per_day}",
            "trades_today": trades_today,
            "minutes_since_last_trade": None
        }
    
    # Check cooldown period
    if last_trade_time:
        minutes_since = (datetime.now() - last_trade_time).total_seconds() / 60
        
        if minutes_since < min_minutes_between_trades:
            return {
                "allowed": False,
                "reason": f"Cooldown period active: {minutes_since:.1f}/{min_minutes_between_trades} minutes",
                "trades_today": trades_today,
                "minutes_since_last_trade": minutes_since
            }
        
        return {
            "allowed": True,
            "reason": "Trading allowed",
            "trades_today": trades_today,
            "minutes_since_last_trade": minutes_since
        }
    
    # No previous trades today
    return {
        "allowed": True,
        "reason": "Trading allowed - no trades today yet",
        "trades_today": trades_today,
        "minutes_since_last_trade": None
    }


def get_trading_stats() -> Dict:
    """Get comprehensive trading statistics"""
    log_data = load_trade_log()
    
    # Calculate stats for last 7 days
    last_7_days = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        last_7_days.append(date)
    
    stats_7d = {
        "total_attempts": 0,
        "successful_trades": 0,
        "rejected_trades": 0
    }
    
    for date in last_7_days:
        if date in log_data["daily_stats"]:
            day_stats = log_data["daily_stats"][date]
            stats_7d["total_attempts"] += day_stats.get("total_attempts", 0)
            stats_7d["successful_trades"] += day_stats.get("successful_trades", 0)
            stats_7d["rejected_trades"] += day_stats.get("rejected_trades", 0)
    
    # Calculate rejection rate
    rejection_rate = 0
    if stats_7d["total_attempts"] > 0:
        rejection_rate = (stats_7d["rejected_trades"] / stats_7d["total_attempts"]) * 100
    
    return {
        "last_7_days": stats_7d,
        "rejection_rate_pct": rejection_rate,
        "avg_trades_per_day": stats_7d["successful_trades"] / 7,
        "today": log_data["daily_stats"].get(datetime.now().strftime("%Y-%m-%d"), {})
    }
