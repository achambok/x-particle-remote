from metatrader import candle_data, symbol_info, tradeable_symbols
from langchain.tools import tool
from typing import Optional
import json


@tool
def get_candle_data_tools(
    symbol: str, timeframe: str, initial_bar_index: int = 0, number_of_bars: int = 100
):
    """
    Retrieve historical candle (OHLCV) data for a symbol and timeframe.

    Args:
        symbol (str): Symbol name (e.g., 'EURUSD'). `tradeable_symbols_tool` can be used to get a list of available symbols.
        timeframe (str):
            MT5 timeframe constants:
                M1: 1 minute (mt5.TIMEFRAME_M1)
                M5: 5 minutes (mt5.TIMEFRAME_M5)
                M15: 15 minutes (mt5.TIMEFRAME_M15)
                M30: 30 minutes (mt5.TIMEFRAME_M30)
                H1: 1 hour (mt5.TIMEFRAME_H1)
                H4: 4 hours (mt5.TIMEFRAME_H4)
                H12: 12 hours (mt5.TIMEFRAME_H12)
                D1: 1 day (mt5.TIMEFRAME_D1)
                W1: 1 week (mt5.TIMEFRAME_W1)
                MN1: 1 month (mt5.TIMEFRAME_MN1)
        initial_bar_index (int): Start index (0 = most recent); default is 0
        number_of_bars (int): Number of bars to fetch; default is 100

    Returns:
        list of dict: Each dict contains keys: time, open, high, low, close, tick_volume, spread, real_volume
    Example:
        [
            {"time": "2025-12-26 16:05:00", "open": 1.17761, "high": 1.17765, ...},
            ...
        ]
    """
    df = candle_data(symbol, timeframe, initial_bar_index, number_of_bars)
    return json.dumps(df, default=str)


@tool
def symbol_info_tool(symbol: str) -> Optional[dict | str]:
    """
    Retrieve detailed MetaTrader 5 symbol information as a dictionary.

    Args:
        symbol (str): Symbol name (e.g., 'EURUSDm')

    Returns:
        dict: Symbol details (bid, ask, point, digits, spread, volume_min, volume_max, etc.)
    Example:
        {
            'symbol': 'EURUSDm', 'bid': 1.17756, 'ask': 1.17758, 'point': 0.00001,
            'digits': 5, 'spread': 2, 'volume_min': 0.01, 'volume_max': 100.0,
            ... (other MetaTrader5 symbol fields)
        }
    """
    return json.dumps(symbol_info(symbol), default=str)


@tool
def tradeable_symbols_tool() -> Optional[list | str]:
    """
    Retrieve a list of all allowed/tradeable symbols and their details.

    Returns:
        list of dict: Each dict contains symbol info (symbol, bid, ask, digits, volume_min, etc.)
    Example:
        [
            {'symbol': 'EURUSDm', 'bid': 1.17756, 'ask': 1.17758, ...},
            {'symbol': 'GBPUSDm', 'bid': 1.37756, 'ask': 1.37758, ...},
            ...
        ]
    """
    return json.dumps(tradeable_symbols(), default=str)
