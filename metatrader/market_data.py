import MetaTrader5 as mt5
import pandas as pd
from .common import ensure_mt5_connection
from typing import Optional, Dict
from config.environments import config


pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1500)


def candle_data(
    symbol: str, timeframe: str, initial_bar_index: int, number_of_bars: int
):
    connected, error = ensure_mt5_connection()
    if not connected:
        return error

    _timeframe = mt5.TIMEFRAME_M1
    if timeframe == "M5":
        _timeframe = mt5.TIMEFRAME_M5
    elif timeframe == "M15":
        _timeframe = mt5.TIMEFRAME_M15
    elif timeframe == "M30":
        _timeframe = mt5.TIMEFRAME_M30
    elif timeframe == "H1":
        _timeframe = mt5.TIMEFRAME_H1
    elif timeframe == "H4":
        _timeframe = mt5.TIMEFRAME_H4
    elif timeframe == "H12":
        _timeframe = mt5.TIMEFRAME_H12
    elif timeframe == "D1":
        _timeframe = mt5.TIMEFRAME_D1
    elif timeframe == "W1":
        _timeframe = mt5.TIMEFRAME_W1
    elif timeframe == "MN1":
        _timeframe = mt5.TIMEFRAME_MN1

    rates = mt5.copy_rates_from_pos(
        symbol, _timeframe, initial_bar_index, number_of_bars
    )

    if rates is None or len(rates) == 0:
        mt5.shutdown()
        return []

    rates_frame = pd.DataFrame(rates)
    if "time" in rates_frame.columns:
        rates_frame["time"] = pd.to_datetime(rates_frame["time"], unit="s")
    mt5.shutdown()

    return rates_frame.to_dict(orient="records")


def symbol_info(symbol: str) -> Optional[Dict | str]:
    connected, error = ensure_mt5_connection()
    if not connected:
        return error

    _symbol_info = mt5.symbol_info(symbol)
    mt5.shutdown()
    if _symbol_info == None:
        return "Symbol info not found"

    return _symbol_info._asdict()


def tradeable_symbols() -> Optional[list | str]:
    connected, error = ensure_mt5_connection()
    if not connected:
        return error

    # Define your symbols
    my_symbols = config.SYMBOLS

    symbols_info = []

    for symbol in my_symbols:
        info = mt5.symbol_info(symbol)
        if info is not None:
            symbols_info.append(info._asdict())

    mt5.shutdown()
    return symbols_info
