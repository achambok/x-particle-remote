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
    off_day = config.OFF_DAYS
    current_day = datetime.now().strftime("%A")

    if current_day in off_day:
        return {
            "trading_allowed": False,
            "message": f"Trading is not allowed on {current_day}s. Because it's an off day.",
        }

    return {"trading_allowed": True, "message": "Trading is allowed today."}


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
