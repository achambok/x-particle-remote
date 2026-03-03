from .common import bridge_get, ensure_mt5_connection
from config.environments import config
from typing import Optional, Dict


def candle_data(symbol: str, timeframe: str, initial_bar_index: int, number_of_bars: int):
    connected, error = ensure_mt5_connection()
    if not connected:
        return error
    try:
        result = bridge_get("/history/prices", params={"symbol": symbol, "time_frame": timeframe})
        if isinstance(result, list):
            return result[-number_of_bars:] if len(result) > number_of_bars else result
        return []
    except Exception:
        return []


def symbol_info(symbol: str) -> Optional[Dict | str]:
    connected, error = ensure_mt5_connection()
    if not connected:
        return error
    try:
        return bridge_get(f"/quote?symbol={symbol}")
    except Exception:
        return "Symbol info not found"


def tradeable_symbols() -> Optional[list | str]:
    connected, error = ensure_mt5_connection()
    if not connected:
        return error
    results = []
    for symbol in config.SYMBOLS:
        try:
            info = bridge_get(f"/quote?symbol={symbol}")
            if info:
                results.append(info)
        except Exception:
            pass
    return results
