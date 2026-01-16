import pandas as pd
import numpy as np
from typing import Optional, Dict, List


def calculate_ema(data: List[Dict], period: int, price_key: str = "close") -> Optional[float]:
    """
    Calculate Exponential Moving Average from candle data.
    
    Args:
        data: List of candle dictionaries with OHLCV data
        period: EMA period (e.g., 50, 200)
        price_key: Which price to use ('close', 'open', 'high', 'low')
        
    Returns:
        float: Current EMA value or None if insufficient data
    """
    if not data or len(data) < period:
        return None
    
    df = pd.DataFrame(data)
    if price_key not in df.columns:
        return None
    
    ema = df[price_key].ewm(span=period, adjust=False).mean()
    return float(ema.iloc[-1])


def calculate_rsi(data: List[Dict], period: int = 14, price_key: str = "close") -> Optional[float]:
    """
    Calculate Relative Strength Index.
    
    Args:
        data: List of candle dictionaries with OHLCV data
        period: RSI period (default 14)
        price_key: Which price to use ('close', 'open', 'high', 'low')
        
    Returns:
        float: Current RSI value (0-100) or None if insufficient data
    """
    if not data or len(data) < period + 1:
        return None
    
    df = pd.DataFrame(data)
    if price_key not in df.columns:
        return None
    
    prices = df[price_key]
    delta = prices.diff()
    
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return float(rsi.iloc[-1])


def calculate_macd(
    data: List[Dict],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    price_key: str = "close"
) -> Optional[Dict[str, float]]:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        data: List of candle dictionaries with OHLCV data
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line period (default 9)
        price_key: Which price to use ('close', 'open', 'high', 'low')
        
    Returns:
        dict: {'macd': float, 'signal': float, 'histogram': float} or None
    """
    if not data or len(data) < slow_period + signal_period:
        return None
    
    df = pd.DataFrame(data)
    if price_key not in df.columns:
        return None
    
    prices = df[price_key]
    
    ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices.ewm(span=slow_period, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return {
        "macd": float(macd_line.iloc[-1]),
        "signal": float(signal_line.iloc[-1]),
        "histogram": float(histogram.iloc[-1])
    }


def calculate_atr(data: List[Dict], period: int = 14) -> Optional[float]:
    """
    Calculate Average True Range (volatility indicator).
    
    Args:
        data: List of candle dictionaries with OHLCV data
        period: ATR period (default 14)
        
    Returns:
        float: Current ATR value or None if insufficient data
    """
    if not data or len(data) < period + 1:
        return None
    
    df = pd.DataFrame(data)
    required_cols = ['high', 'low', 'close']
    if not all(col in df.columns for col in required_cols):
        return None
    
    high = df['high']
    low = df['low']
    close = df['close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period, min_periods=period).mean()
    
    return float(atr.iloc[-1])


def calculate_bollinger_bands(
    data: List[Dict],
    period: int = 20,
    std_dev: float = 2.0,
    price_key: str = "close"
) -> Optional[Dict[str, float]]:
    """
    Calculate Bollinger Bands.
    
    Args:
        data: List of candle dictionaries with OHLCV data
        period: Moving average period (default 20)
        std_dev: Standard deviation multiplier (default 2.0)
        price_key: Which price to use ('close', 'open', 'high', 'low')
        
    Returns:
        dict: {'upper': float, 'middle': float, 'lower': float, 'bandwidth': float} or None
    """
    if not data or len(data) < period:
        return None
    
    df = pd.DataFrame(data)
    if price_key not in df.columns:
        return None
    
    prices = df[price_key]
    
    middle_band = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    bandwidth = ((upper_band - lower_band) / middle_band) * 100
    
    return {
        "upper": float(upper_band.iloc[-1]),
        "middle": float(middle_band.iloc[-1]),
        "lower": float(lower_band.iloc[-1]),
        "bandwidth": float(bandwidth.iloc[-1])
    }


def calculate_support_resistance(
    data: List[Dict],
    lookback: int = 20,
    tolerance: float = 0.0001
) -> Dict[str, List[float]]:
    """
    Identify support and resistance levels using pivot points.
    
    Args:
        data: List of candle dictionaries with OHLCV data
        lookback: Number of bars to look back for pivot points
        tolerance: Price tolerance for level clustering
        
    Returns:
        dict: {'support': [prices], 'resistance': [prices]}
    """
    if not data or len(data) < lookback + 2:
        return {"support": [], "resistance": []}
    
    df = pd.DataFrame(data)
    
    highs = df['high'].values
    lows = df['low'].values
    
    resistance_levels = []
    support_levels = []
    
    # Find pivot highs (resistance)
    for i in range(lookback, len(highs) - lookback):
        if highs[i] == max(highs[i-lookback:i+lookback+1]):
            resistance_levels.append(highs[i])
    
    # Find pivot lows (support)
    for i in range(lookback, len(lows) - lookback):
        if lows[i] == min(lows[i-lookback:i+lookback+1]):
            support_levels.append(lows[i])
    
    # Cluster nearby levels
    def cluster_levels(levels, tolerance):
        if not levels:
            return []
        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_cluster[-1]) <= tolerance:
                current_cluster.append(level)
            else:
                clustered.append(sum(current_cluster) / len(current_cluster))
                current_cluster = [level]
        
        clustered.append(sum(current_cluster) / len(current_cluster))
        return clustered
    
    return {
        "support": cluster_levels(support_levels, tolerance),
        "resistance": cluster_levels(resistance_levels, tolerance)
    }


def calculate_pip_value(symbol: str, volume: float) -> float:
    """
    Calculate pip value for a given symbol and volume.
    
    Args:
        symbol: Trading symbol (e.g., 'EURUSDm')
        volume: Lot size
        
    Returns:
        float: Pip value in account currency
    """
    # Standard forex pairs: 1 pip = 0.0001 for most pairs, 0.01 for JPY pairs
    if 'JPY' in symbol:
        pip_multiplier = 0.01
    else:
        pip_multiplier = 0.0001
    
    # Standard lot size is 100,000 units
    standard_lot = 100000
    pip_value = volume * standard_lot * pip_multiplier
    
    return pip_value


def calculate_position_size(
    account_balance: float,
    risk_percentage: float,
    stop_loss_pips: float,
    symbol: str
) -> Dict[str, float]:
    """
    Calculate optimal position size based on risk parameters.
    
    Args:
        account_balance: Current account balance
        risk_percentage: Risk per trade as percentage (e.g., 4 for 4%)
        stop_loss_pips: Stop loss distance in pips
        symbol: Trading symbol
        
    Returns:
        dict: {'volume': float, 'risk_amount': float, 'pip_value': float}
    """
    risk_amount = account_balance * (risk_percentage / 100)
    
    # Calculate pip value per standard lot
    if 'JPY' in symbol:
        pip_multiplier = 0.01
    else:
        pip_multiplier = 0.0001
    
    standard_lot = 100000
    pip_value_per_lot = standard_lot * pip_multiplier
    
    # Calculate required volume
    volume = risk_amount / (stop_loss_pips * pip_value_per_lot)
    
    # Round to 2 decimal places and enforce minimum
    volume = max(0.01, round(volume, 2))
    
    return {
        "volume": volume,
        "risk_amount": risk_amount,
        "pip_value": pip_value_per_lot * volume
    }
