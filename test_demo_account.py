#!/usr/bin/env python3
"""
Test script to verify MT5 demo account connection and trading capabilities
"""

import MetaTrader5 as mt5
from config.environments import config
from metatrader.account_info import account_info, allow_trading
from metatrader.market_data import candle_data
from metatrader.metatrader import send_order, close_order

def test_demo_account():
    """Test MT5 demo account connection and trading"""
    print("=== MT5 Demo Account Test ===")
    
    # Test 1: Initialize MT5
    print("1. Testing MT5 initialization...")
    if mt5.initialize():
        print("   OK MT5 initialized successfully")
    else:
        print(f"   ERROR MT5 initialization failed: {mt5.last_error()}")
        return False
    
    # Test 2: Get account info
    print("\n2. Testing account information...")
    acct_info = account_info()
    if acct_info.get("success"):
        print(f"   OK Account connected: {acct_info.get('login')}")
        print(f"   OK Balance: {acct_info.get('balance')} {acct_info.get('currency')}")
        print(f"   OK Equity: {acct_info.get('equity')}")
        print(f"   OK Leverage: {acct_info.get('leverage')}")
        print(f"   OK Trading allowed: {acct_info.get('trade_allowed')}")
        print(f"   OK Trading mode: {acct_info.get('trade_mode')}")
    else:
        print(f"   ERROR Account info failed: {acct_info.get('error')}")
    
    # Test 3: Check trading permissions
    print("\n3. Testing trading permissions...")
    trading_status = allow_trading()
    if isinstance(trading_status, dict):
        print(f"   OK Trading allowed: {trading_status.get('trading_allowed')}")
        print(f"   OK Market status: {trading_status.get('market_status')}")
        if not trading_status.get('trading_allowed'):
            print(f"   OK Reason: {trading_status.get('message')}")
    else:
        print(f"   ERROR Trading status check failed: {trading_status}")
    
    # Test 4: Test market data
    print("\n4. Testing market data access...")
    symbol = config.SYMBOLS[0]  # EURUSDm
    data = candle_data(symbol, "M1", 0, 10)
    if data:
        print(f"   OK {symbol} data: {len(data)} candles retrieved")
        latest_candle = data[-1]
        print(f"   OK Latest price: {latest_candle.get('close')}")
    else:
        print(f"   ERROR {symbol} data failed")
    
    # Test 5: Test symbol info
    print("\n5. Testing symbol information...")
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info:
        print(f"   OK Symbol: {symbol_info.name}")
        print(f"   OK Point size: {symbol_info.point}")
        print(f"   OK Trade allowed: {symbol_info.trade_mode}")
        print(f"   OK Volume min: {symbol_info.volume_min}")
        print(f"   OK Volume max: {symbol_info.volume_max}")
        print(f"   OK Volume step: {symbol_info.volume_step}")
    else:
        print(f"   ERROR Symbol info failed for {symbol}")
    
    # Test 6: Test a small demo trade (if trading is allowed)
    print("\n6. Testing demo trade capability...")
    trading_allowed = False
    if isinstance(trading_status, dict):
        trading_allowed = trading_status.get('trading_allowed', False)
    
    if trading_allowed and acct_info.get('trade_allowed'):
        try:
            # Test sending a small buy order
            result = send_order(
                symbol=symbol,
                volume=0.01,  # Very small volume for demo
                deviation=20,
                order_type="BUY",
                sl_points=50,  # 50 points SL
                tp_points=100,  # 100 points TP
                comment="Test order from X-Particle"
            )
            
            if result.get("success"):
                print(f"   OK Test order placed successfully!")
                print(f"   OK Ticket: {result.get('ticket')}")
                print(f"   OK Volume: {result.get('volume')}")
                print(f"   OK Price: {result.get('price')}")
                
                # Test closing the order
                ticket = result.get('ticket')
                if ticket:
                    close_result = close_order(ticket, deviation=20)
                    if close_result.get("success"):
                        print(f"   OK Test order closed successfully!")
                    else:
                        print(f"   ERROR Order close failed: {close_result.get('error')}")
            else:
                print(f"   ERROR Test order failed: {result.get('error')}")
                
        except Exception as e:
            print(f"   ERROR Demo trade test error: {e}")
    else:
        print("   ERROR Trading not allowed - skipping demo trade test")
    
    # Shutdown MT5
    mt5.shutdown()
    print("\n   OK MT5 shutdown completed")
    return True

if __name__ == "__main__":
    test_demo_account()