from .common import bridge_get, ensure_mt5_connection
from datetime import datetime
import re, os


def account_info() -> dict:
    connected, error = ensure_mt5_connection()
    if not connected:
        return {"success": False, "error": error}
    return bridge_get("/account")


def terminal_info() -> dict:
    connected, error = ensure_mt5_connection()
    if not connected:
        return {"success": False, "error": error}
    return bridge_get("/account")


def allow_trading() -> dict:
    from zoneinfo import ZoneInfo
    est_tz = ZoneInfo("America/New_York")
    now_est = datetime.now(est_tz)
    current_day = now_est.strftime("%A")
    current_hour = now_est.hour
    market_open = True
    next_open = None
    close_reason = None
    if current_day == "Saturday":
        market_open = False
        close_reason = "Weekend - Market closed all day Saturday"
        next_open = "Sunday 5:00 PM EST"
    elif current_day == "Sunday" and current_hour < 17:
        market_open = False
        close_reason = "Weekend - Market opens Sunday 5:00 PM EST"
        next_open = f"Today at 5:00 PM EST (in ~{17 - current_hour} hours)"
    elif current_day == "Friday" and current_hour >= 17:
        market_open = False
        close_reason = "Weekend - Market closed Friday 5:00 PM EST"
        next_open = "Sunday 5:00 PM EST"
    if market_open:
        return {"trading_allowed": True, "message": "Forex market is OPEN.", "market_status": "OPEN",
                "current_time_est": now_est.strftime("%Y-%m-%d %H:%M EST"), "current_day": current_day,
                "session_info": _get_trading_session(current_hour)}
    return {"trading_allowed": False, "message": close_reason, "market_status": "CLOSED_WEEKEND",
            "current_time_est": now_est.strftime("%Y-%m-%d %H:%M EST"), "current_day": current_day, "next_open": next_open}


def _get_trading_session(hour_est: int) -> str:
    sessions = []
    if hour_est >= 17 or hour_est < 2: sessions.append("Sydney")
    if hour_est >= 19 or hour_est < 4: sessions.append("Tokyo")
    if 3 <= hour_est < 12: sessions.append("London")
    if 8 <= hour_est < 17: sessions.append("New York")
    if not sessions: return "Low liquidity period"
    if len(sessions) >= 2: return f"Session overlap: {' + '.join(sessions)} (HIGH LIQUIDITY)"
    return f"{sessions[0]} session active"


def agent_runner_logger_info(index: int = 0):
    log_file_path = os.path.join("logs", "agent.log")
    if not os.path.exists(log_file_path):
        return {"success": False, "error": f"Log file not found at {log_file_path}"}
    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        log_pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \| \w+ \|", re.MULTILINE)
        matches = list(log_pattern.finditer(content))
        if not matches:
            return {"success": False, "error": "No log entries found"}
        log_entries = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            log_entries.append(content[start:end].strip())
        log_entries.reverse()
        if index < 0 or index >= len(log_entries):
            return {"success": False, "error": f"Index {index} out of range. Total: {len(log_entries)}"}
        return {"success": True, "log_entry": log_entries[index], "index": index, "total_entries": len(log_entries)}
    except Exception as e:
        return {"success": False, "error": str(e)}
