import MetaTrader5 as mt5
from .common import ensure_mt5_connection
from datetime import datetime
from config.environments import config
import os


def account_info() -> dict:
    connected, error = ensure_mt5_connection()
    if not connected:
        return {"success": False, "error": error}

    info = mt5.account_info()
    if info is None:
        return {
            "success": False,
            "error": "Failed to retrieve account information.",
        }

    return info._asdict()


def terminal_info():
    connected, error = ensure_mt5_connection()
    if not connected:
        return {"success": False, "error": error}

    info = mt5.terminal_info()
    if info is None:
        return {
            "success": False,
            "message": "Failed to retrieve terminal information.",
            "error": mt5.last_error(),
        }

    return info._asdict()


def allow_trading():
    """
    Check if Forex market is currently open.

    Forex Market Hours:
    - Opens: Sunday 5:00 PM EST (22:00 UTC)
    - Closes: Friday 5:00 PM EST (22:00 UTC)

    Returns:
        dict: {'trading_allowed': bool, 'message': str, 'market_status': str, 'next_open': str}
    """
    from zoneinfo import ZoneInfo

    # Get current time in EST (Eastern Standard Time)
    est_tz = ZoneInfo("America/New_York")
    now_est = datetime.now(est_tz)

    current_day = now_est.strftime("%A")
    current_hour = now_est.hour

    # Forex Market Hours Logic
    # CLOSED: Friday 5PM EST to Sunday 5PM EST
    # OPEN: Sunday 5PM EST to Friday 5PM EST

    market_open = True
    next_open = None
    close_reason = None

    if current_day == "Saturday":
        # Saturday: Market always closed
        market_open = False
        close_reason = "Weekend - Market closed all day Saturday"
        next_open = "Sunday 5:00 PM EST"

    elif current_day == "Sunday":
        # Sunday: Closed until 5PM EST
        if current_hour < 17:
            market_open = False
            close_reason = "Weekend - Market opens Sunday 5:00 PM EST"
            hours_until_open = 17 - current_hour
            next_open = f"Today at 5:00 PM EST (in ~{hours_until_open} hours)"
        else:
            # Sunday after 5PM - market is open
            market_open = True

    elif current_day == "Friday":
        # Friday: Open until 5PM EST
        if current_hour >= 17:
            market_open = False
            close_reason = "Weekend - Market closed Friday 5:00 PM EST"
            next_open = "Sunday 5:00 PM EST"
        else:
            market_open = True

    else:
        # Monday to Thursday: Market open 24 hours
        market_open = True

    if market_open:
        # Calculate time until market closes (Friday 5PM EST)
        days_until_friday = (4 - now_est.weekday()) % 7  # Friday is weekday 4
        if days_until_friday == 0 and current_hour >= 17:
            days_until_friday = 7

        return {
            "trading_allowed": True,
            "message": "Forex market is OPEN. Trading allowed.",
            "market_status": "OPEN",
            "current_time_est": now_est.strftime("%Y-%m-%d %H:%M EST"),
            "current_day": current_day,
            "closes": "Friday 5:00 PM EST",
            "session_info": _get_trading_session(current_hour),
        }
    else:
        return {
            "trading_allowed": False,
            "message": close_reason,
            "market_status": "CLOSED_WEEKEND",
            "current_time_est": now_est.strftime("%Y-%m-%d %H:%M EST"),
            "current_day": current_day,
            "next_open": next_open,
        }


def _get_trading_session(hour_est: int) -> str:
    """
    Determine which major trading session is currently active.

    Sessions (in EST):
    - Sydney: 5PM - 2AM EST
    - Tokyo: 7PM - 4AM EST
    - London: 3AM - 12PM EST
    - New York: 8AM - 5PM EST

    Best trading times are during session overlaps.
    """
    sessions = []

    # Sydney session: 5PM - 2AM EST
    if hour_est >= 17 or hour_est < 2:
        sessions.append("Sydney")

    # Tokyo session: 7PM - 4AM EST
    if hour_est >= 19 or hour_est < 4:
        sessions.append("Tokyo")

    # London session: 3AM - 12PM EST
    if 3 <= hour_est < 12:
        sessions.append("London")

    # New York session: 8AM - 5PM EST
    if 8 <= hour_est < 17:
        sessions.append("New York")

    if not sessions:
        return "Low liquidity period"
    elif len(sessions) >= 2:
        return f"Session overlap: {' + '.join(sessions)} (HIGH LIQUIDITY)"
    else:
        return f"{sessions[0]} session active"


def agent_runner_logger_info(index: int = 0):
    import re

    log_file_path = os.path.join("logs", "agent.log")

    if not os.path.exists(log_file_path):
        return {
            "success": False,
            "error": f"Log file not found at {log_file_path}",
        }

    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Pattern to match log entry start: YYYY-MM-DD HH:MM:SS,mmm | LEVEL |
        log_pattern = re.compile(
            r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \| \w+ \|", re.MULTILINE
        )

        # Find all log entry start positions
        matches = list(log_pattern.finditer(content))

        if not matches:
            return {
                "success": False,
                "error": "No log entries found in the file",
            }

        # Extract each complete log entry (including multi-line messages)
        log_entries = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            log_entry = content[start:end].strip()
            log_entries.append(log_entry)

        # Reverse to get descending order (newest first)
        log_entries.reverse()

        if index < 0 or index >= len(log_entries):
            return {
                "success": False,
                "error": f"Index {index} out of range. Total entries: {len(log_entries)}",
            }

        return {
            "success": True,
            "log_entry": log_entries[index],
            "index": index,
            "total_entries": len(log_entries),
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read log file: {str(e)}",
        }
