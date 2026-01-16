from metatrader import (
    candle_data,
    symbol_info,
    active_positions,
    active_orders_count,
)
from metatrader.indicators import (
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_atr,
    calculate_bollinger_bands,
    calculate_support_resistance,
    calculate_position_size,
)
from langchain.tools import tool
from typing import Optional
import json


@tool
def calculate_technical_indicators_tool(
    symbol: str,
    timeframe: str = "H1",
    number_of_bars: int = 200
) -> dict:
    """
    Calculate comprehensive technical indicators for a symbol.
    
    Args:
        symbol (str): Trading symbol (e.g., 'EURUSDm')
        timeframe (str): Timeframe (M15, H1, H4, D1)
        number_of_bars (int): Number of bars to analyze (default 200)
        
    Returns:
        dict: Complete technical analysis including:
            - ema_50, ema_200 (trend)
            - rsi (momentum, 0-100)
            - macd (macd, signal, histogram)
            - atr (volatility in pips)
            - bollinger_bands (upper, middle, lower)
            - support_resistance levels
            - trend_direction (BULLISH, BEARISH, NEUTRAL)
            - momentum_state (OVERSOLD, OVERBOUGHT, NEUTRAL)
    """
    # Get candle data
    data = candle_data(symbol, timeframe, 0, number_of_bars)
    
    if not data or len(data) < 200:
        return json.dumps({
            "error": "Insufficient candle data for analysis",
            "symbol": symbol,
            "timeframe": timeframe
        }, default=str)
    
    # Calculate indicators
    ema_50 = calculate_ema(data, 50)
    ema_200 = calculate_ema(data, 200)
    rsi = calculate_rsi(data, 14)
    macd = calculate_macd(data)
    atr = calculate_atr(data, 14)
    bollinger = calculate_bollinger_bands(data, 20)
    support_resistance = calculate_support_resistance(data, 20)
    
    # Get current price
    current_price = data[-1].get('close', 0)
    
    # Determine trend
    trend_direction = "NEUTRAL"
    if ema_50 and ema_200:
        if ema_50 > ema_200 and current_price > ema_50:
            trend_direction = "BULLISH"
        elif ema_50 < ema_200 and current_price < ema_50:
            trend_direction = "BEARISH"
    
    # Determine momentum state
    momentum_state = "NEUTRAL"
    if rsi:
        if rsi < 30:
            momentum_state = "OVERSOLD"
        elif rsi > 70:
            momentum_state = "OVERBOUGHT"
    
    # MACD signal
    macd_signal = "NEUTRAL"
    if macd:
        if macd['histogram'] > 0 and macd['macd'] > macd['signal']:
            macd_signal = "BULLISH"
        elif macd['histogram'] < 0 and macd['macd'] < macd['signal']:
            macd_signal = "BEARISH"
    
    # Bollinger Bands position
    bb_position = "NEUTRAL"
    if bollinger:
        if current_price < bollinger['lower']:
            bb_position = "BELOW_LOWER_BAND"
        elif current_price > bollinger['upper']:
            bb_position = "ABOVE_UPPER_BAND"
        elif current_price > bollinger['middle']:
            bb_position = "ABOVE_MIDDLE"
        else:
            bb_position = "BELOW_MIDDLE"
    
    result = {
        "symbol": symbol,
        "timeframe": timeframe,
        "current_price": current_price,
        "indicators": {
            "ema_50": ema_50,
            "ema_200": ema_200,
            "rsi": rsi,
            "macd": macd,
            "atr_pips": atr / 0.0001 if atr else None,  # Convert to pips
            "atr_price": atr,
            "bollinger_bands": bollinger,
        },
        "analysis": {
            "trend_direction": trend_direction,
            "momentum_state": momentum_state,
            "macd_signal": macd_signal,
            "bb_position": bb_position,
        },
        "levels": {
            "support": support_resistance['support'][-3:] if support_resistance['support'] else [],
            "resistance": support_resistance['resistance'][-3:] if support_resistance['resistance'] else [],
        }
    }
    
    return json.dumps(result, default=str)


@tool
def calculate_optimal_position_size_tool(
    symbol: str,
    stop_loss_pips: float,
    risk_percentage: float = 4.0
) -> dict:
    """
    Calculate optimal position size based on risk management rules.
    
    Args:
        symbol (str): Trading symbol (e.g., 'EURUSDm')
        stop_loss_pips (float): Stop loss distance in pips
        risk_percentage (float): Risk per trade as percentage (default 4%)
        
    Returns:
        dict: Position sizing details including:
            - recommended_volume (float): Lot size to use
            - risk_amount (float): Dollar amount at risk
            - pip_value (float): Value per pip movement
            - account_balance (float): Current balance used for calculation
    """
    from metatrader import account_info as get_account_info
    
    # Get current account balance
    account_data = get_account_info()
    
    if not isinstance(account_data, dict) or 'balance' not in account_data:
        return json.dumps({
            "error": "Failed to retrieve account information",
            "recommended_volume": 0.01
        }, default=str)
    
    balance = account_data['balance']
    
    # Calculate position size
    sizing = calculate_position_size(
        account_balance=balance,
        risk_percentage=risk_percentage,
        stop_loss_pips=stop_loss_pips,
        symbol=symbol
    )
    
    result = {
        "symbol": symbol,
        "account_balance": balance,
        "risk_percentage": risk_percentage,
        "stop_loss_pips": stop_loss_pips,
        "recommended_volume": sizing['volume'],
        "risk_amount": sizing['risk_amount'],
        "pip_value": sizing['pip_value'],
        "calculation": f"Risk ${sizing['risk_amount']:.2f} ({risk_percentage}%) / {stop_loss_pips} pips = {sizing['volume']} lots"
    }
    
    return json.dumps(result, default=str)


@tool
def validate_trade_setup_tool(
    symbol: str,
    order_type: str,
    stop_loss_pips: float,
    take_profit_pips: float
) -> dict:
    """
    Validate if a trade setup meets quality and risk management criteria.
    
    Args:
        symbol (str): Trading symbol
        order_type (str): 'BUY' or 'SELL'
        stop_loss_pips (float): Proposed stop loss in pips
        take_profit_pips (float): Proposed take profit in pips
        
    Returns:
        dict: Validation results including:
            - is_valid (bool): Whether trade setup passes validation
            - validation_checks (dict): Individual check results
            - warnings (list): Any warnings about the setup
            - recommendations (list): Suggestions for improvement
    """
    warnings = []
    recommendations = []
    checks = {}
    
    # Get symbol info for spread
    sym_info = symbol_info(symbol)
    if isinstance(sym_info, dict):
        spread_pips = sym_info.get('spread', 0)
    else:
        spread_pips = 10  # Conservative estimate if unavailable
        warnings.append("Could not retrieve spread, using conservative estimate of 10 pips")
    
    # Check 1: Risk-Reward Ratio (minimum 1:3)
    rr_ratio = take_profit_pips / stop_loss_pips if stop_loss_pips > 0 else 0
    checks['risk_reward_ratio'] = {
        "value": rr_ratio,
        "passed": rr_ratio >= 3.0,
        "requirement": "Minimum 1:3"
    }
    
    if rr_ratio < 3.0:
        warnings.append(f"Risk-reward ratio {rr_ratio:.2f} is below minimum 1:3")
        recommendations.append(f"Increase TP to at least {stop_loss_pips * 3:.1f} pips for 1:3 ratio")
    
    # Check 2: Stop Loss vs Spread (SL should be > 3x spread)
    checks['stop_loss_vs_spread'] = {
        "stop_loss_pips": stop_loss_pips,
        "spread_pips": spread_pips,
        "ratio": stop_loss_pips / spread_pips if spread_pips > 0 else 0,
        "passed": stop_loss_pips > (spread_pips * 3),
        "requirement": "SL > 3x spread"
    }
    
    if stop_loss_pips <= (spread_pips * 3):
        warnings.append(f"Stop loss {stop_loss_pips} pips is too tight relative to {spread_pips} pip spread")
        recommendations.append(f"Increase SL to minimum {spread_pips * 3:.1f} pips")
    
    # Check 3: Minimum stop loss (should be >= 10 pips)
    checks['minimum_stop_loss'] = {
        "value": stop_loss_pips,
        "passed": stop_loss_pips >= 10,
        "requirement": "Minimum 10 pips"
    }
    
    if stop_loss_pips < 10:
        warnings.append(f"Stop loss {stop_loss_pips} pips is too tight, vulnerable to market noise")
        recommendations.append("Use minimum 10 pips SL, ideally ATR-based SL")
    
    # Check 4: Check for existing positions on this symbol
    positions = active_positions()
    position_count = 0
    
    if isinstance(positions, str) and symbol in positions:
        # Parse the string to count positions (rough check)
        position_count = positions.count(symbol)
        checks['existing_positions'] = {
            "count": position_count,
            "passed": position_count == 0,
            "requirement": "No existing positions on symbol"
        }
        
        if position_count > 0:
            warnings.append(f"Already have {position_count} position(s) on {symbol}")
            recommendations.append("Avoid adding to existing positions, manage current positions first")
    else:
        checks['existing_positions'] = {
            "count": 0,
            "passed": True,
            "requirement": "No existing positions on symbol"
        }
    
    # Check 5: Spread-adjusted Risk-Reward
    effective_sl = stop_loss_pips + spread_pips
    effective_tp = take_profit_pips - spread_pips
    effective_rr = effective_tp / effective_sl if effective_sl > 0 else 0
    
    checks['spread_adjusted_rr'] = {
        "value": effective_rr,
        "passed": effective_rr >= 2.5,
        "requirement": "Minimum 2.5:1 after spread"
    }
    
    if effective_rr < 2.5:
        warnings.append(f"After spread adjustment, RR is only {effective_rr:.2f}")
        recommendations.append("Spread costs significantly impact this trade, consider wider targets")
    
    # Overall validation
    is_valid = all(check.get('passed', False) for check in checks.values())
    
    result = {
        "symbol": symbol,
        "order_type": order_type,
        "is_valid": is_valid,
        "validation_checks": checks,
        "warnings": warnings,
        "recommendations": recommendations,
        "summary": "Trade setup PASSED validation" if is_valid else "Trade setup FAILED validation - do not trade"
    }
    
    return json.dumps(result, default=str)


@tool
def check_trading_conditions_tool() -> dict:
    """
    Check overall trading conditions and restrictions.
    
    Returns:
        dict: Trading conditions including:
            - can_trade (bool): Whether trading should proceed
            - active_positions_count (int): Current open positions
            - reasons (list): Reasons why trading may be restricted
            - account_health (dict): Account metrics
    """
    from metatrader import account_info as get_account_info, allow_trading
    
    reasons = []
    can_trade = True
    
    # Check if trading is allowed today (off days)
    trading_allowed = allow_trading()
    if not trading_allowed.get('trading_allowed', False):
        can_trade = False
        reasons.append(trading_allowed.get('message', 'Trading not allowed today'))
    
    # Get account info
    account_data = get_account_info()
    
    if isinstance(account_data, dict):
        balance = account_data.get('balance', 0)
        equity = account_data.get('equity', 0)
        margin_level = account_data.get('margin_level', 0)
        profit = account_data.get('profit', 0)
        
        # Check account health
        if equity < balance * 0.95:
            reasons.append(f"Account is in drawdown: Equity ${equity:.2f} vs Balance ${balance:.2f}")
        
        if margin_level > 0 and margin_level < 200:
            can_trade = False
            reasons.append(f"Margin level too low: {margin_level:.1f}% (minimum 200%)")
        
        account_health = {
            "balance": balance,
            "equity": equity,
            "profit": profit,
            "margin_level": margin_level,
            "drawdown_pct": ((balance - equity) / balance * 100) if balance > 0 else 0
        }
    else:
        account_health = {"error": "Could not retrieve account information"}
        reasons.append("Failed to retrieve account information")
    
    # Check number of active positions
    positions_count = active_orders_count()
    
    if isinstance(positions_count, int):
        if positions_count >= 3:
            can_trade = False
            reasons.append(f"Maximum concurrent positions reached: {positions_count}/3")
        
        account_health['active_positions'] = positions_count
    
    result = {
        "can_trade": can_trade,
        "timestamp": pd.Timestamp.now().isoformat(),
        "reasons": reasons if reasons else ["All conditions met for trading"],
        "account_health": account_health,
        "recommendation": "Proceed with trade validation" if can_trade else "Do not trade - wait for better conditions"
    }
    
    return json.dumps(result, default=str)


import pandas as pd
