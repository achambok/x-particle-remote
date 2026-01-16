from metatrader import candle_data, symbol_info
from metatrader.indicators import calculate_atr
from langchain.tools import tool
import json


@tool
def calculate_atr_based_stops_tool(
    symbol: str,
    timeframe: str = "H1",
    atr_multiplier: float = 2.0,
    order_type: str = "BUY"
) -> dict:
    """
    Calculate ATR-based stop loss and take profit levels.
    
    Uses Average True Range (volatility) to set dynamic stops that adapt to market conditions.
    
    Args:
        symbol (str): Trading symbol (e.g., 'EURUSDm')
        timeframe (str): Timeframe for ATR calculation (default 'H1')
        atr_multiplier (float): Multiplier for ATR (default 2.0 for SL, 6.0 for TP)
        order_type (str): 'BUY' or 'SELL'
        
    Returns:
        dict: ATR-based stop and target levels including:
            - atr_value (float): Current ATR in pips
            - stop_loss_pips (float): Recommended SL distance in pips
            - take_profit_pips (float): Recommended TP distance in pips (3x SL)
            - stop_loss_price (float): Actual SL price level
            - take_profit_price (float): Actual TP price level
            - current_price (float): Current market price
            - risk_reward_ratio (float): Calculated RR ratio
    """
    # Get candle data for ATR calculation
    data = candle_data(symbol, timeframe, 0, 50)
    
    if not data or len(data) < 20:
        return json.dumps({
            "error": "Insufficient candle data for ATR calculation",
            "symbol": symbol
        }, default=str)
    
    # Calculate ATR
    atr_value = calculate_atr(data, period=14)
    
    if not atr_value:
        return json.dumps({
            "error": "Failed to calculate ATR",
            "symbol": symbol
        }, default=str)
    
    # Convert ATR to pips
    if 'JPY' in symbol:
        atr_pips = atr_value / 0.01
    else:
        atr_pips = atr_value / 0.0001
    
    # Calculate stop loss (ATR * multiplier)
    stop_loss_pips = atr_pips * atr_multiplier
    
    # Ensure minimum stop loss (10 pips)
    stop_loss_pips = max(stop_loss_pips, 10.0)
    
    # Get symbol info for current price and spread
    sym_info = symbol_info(symbol)
    
    if isinstance(sym_info, dict):
        current_price = sym_info.get('bid', 0) if order_type == "SELL" else sym_info.get('ask', 0)
        spread_pips = sym_info.get('spread', 0)
        point = sym_info.get('point', 0.0001)
    else:
        return json.dumps({
            "error": "Failed to get symbol information",
            "symbol": symbol
        }, default=str)
    
    # Adjust stop loss for spread (add spread to SL)
    effective_stop_loss_pips = stop_loss_pips + spread_pips
    
    # Calculate take profit (3x stop loss minimum, adjusted for spread)
    take_profit_pips = (effective_stop_loss_pips * 3) - spread_pips
    
    # Ensure minimum RR ratio of 1:3
    if take_profit_pips < stop_loss_pips * 3:
        take_profit_pips = stop_loss_pips * 3
    
    # Calculate actual price levels
    if order_type == "BUY":
        stop_loss_price = current_price - (stop_loss_pips * point)
        take_profit_price = current_price + (take_profit_pips * point)
    else:  # SELL
        stop_loss_price = current_price + (stop_loss_pips * point)
        take_profit_price = current_price - (take_profit_pips * point)
    
    # Calculate risk-reward ratio
    rr_ratio = take_profit_pips / stop_loss_pips if stop_loss_pips > 0 else 0
    
    result = {
        "symbol": symbol,
        "timeframe": timeframe,
        "order_type": order_type,
        "current_price": current_price,
        "atr": {
            "value_price": atr_value,
            "value_pips": atr_pips,
            "period": 14,
            "multiplier": atr_multiplier
        },
        "spread_pips": spread_pips,
        "stop_loss": {
            "pips": stop_loss_pips,
            "price": stop_loss_price,
            "distance_from_entry": stop_loss_pips
        },
        "take_profit": {
            "pips": take_profit_pips,
            "price": take_profit_price,
            "distance_from_entry": take_profit_pips
        },
        "risk_reward_ratio": rr_ratio,
        "recommendation": f"Use ATR-based SL of {stop_loss_pips:.1f} pips and TP of {take_profit_pips:.1f} pips for {symbol}",
        "notes": [
            f"ATR adapts to market volatility: {atr_pips:.1f} pips",
            f"Spread-adjusted: +{spread_pips} pips added to effective SL",
            f"Minimum 1:3 RR ratio maintained: {rr_ratio:.2f}"
        ]
    }
    
    return json.dumps(result, default=str)


@tool
def recommend_trade_parameters_tool(
    symbol: str,
    order_type: str,
    timeframe: str = "H1"
) -> dict:
    """
    Get complete recommended trade parameters including position size, SL, TP based on ATR and risk management.
    
    This is the RECOMMENDED tool to use before placing any trade. It provides everything needed.
    
    Args:
        symbol (str): Trading symbol (e.g., 'EURUSDm')
        order_type (str): 'BUY' or 'SELL'
        timeframe (str): Timeframe for analysis (default 'H1')
        
    Returns:
        dict: Complete trade parameters including:
            - recommended_volume (float): Position size in lots
            - stop_loss_pips (float): SL distance in pips
            - take_profit_pips (float): TP distance in pips
            - stop_loss_price (float): SL price level
            - take_profit_price (float): TP price level
            - risk_amount (float): Dollar amount at risk
            - risk_percentage (float): Risk as % of balance
            - risk_reward_ratio (float): RR ratio
    """
    from metatrader import account_info as get_account_info
    from metatrader.indicators import calculate_position_size
    
    # Get ATR-based stops
    atr_stops_data = calculate_atr_based_stops_tool.invoke({
        "symbol": symbol,
        "timeframe": timeframe,
        "atr_multiplier": 2.0,
        "order_type": order_type
    })
    
    atr_stops = json.loads(atr_stops_data)
    
    if "error" in atr_stops:
        return json.dumps(atr_stops, default=str)
    
    # Get account balance
    account_data = get_account_info()
    if not isinstance(account_data, dict) or 'balance' not in account_data:
        return json.dumps({
            "error": "Failed to retrieve account information"
        }, default=str)
    
    balance = account_data['balance']
    
    # Calculate position size with 4% risk
    stop_loss_pips = atr_stops['stop_loss']['pips']
    
    sizing = calculate_position_size(
        account_balance=balance,
        risk_percentage=4.0,
        stop_loss_pips=stop_loss_pips,
        symbol=symbol
    )
    
    result = {
        "symbol": symbol,
        "order_type": order_type,
        "timeframe": timeframe,
        "account_balance": balance,
        "recommended_parameters": {
            "volume": sizing['volume'],
            "stop_loss_pips": stop_loss_pips,
            "take_profit_pips": atr_stops['take_profit']['pips'],
            "deviation": 20
        },
        "price_levels": {
            "entry": atr_stops['current_price'],
            "stop_loss": atr_stops['stop_loss']['price'],
            "take_profit": atr_stops['take_profit']['price']
        },
        "risk_management": {
            "risk_amount": sizing['risk_amount'],
            "risk_percentage": 4.0,
            "pip_value": sizing['pip_value'],
            "risk_reward_ratio": atr_stops['risk_reward_ratio']
        },
        "atr_info": atr_stops['atr'],
        "summary": f"Trade {symbol} {order_type} with {sizing['volume']} lots, SL: {stop_loss_pips:.1f} pips, TP: {atr_stops['take_profit']['pips']:.1f} pips, Risk: ${sizing['risk_amount']:.2f} (4%)",
        "validation_notes": [
            "ATR-based stops adapt to market volatility",
            "4% risk per trade as per risk management rules",
            f"Risk-reward ratio: {atr_stops['risk_reward_ratio']:.2f}:1",
            "Position size calculated dynamically based on account balance"
        ]
    }
    
    return json.dumps(result, default=str)
