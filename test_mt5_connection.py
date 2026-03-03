#!/usr/bin/env python3
"""
Test script to verify MT5 connection and data access
"""

import MetaTrader5 as mt5
from config.environments import config
from metatrader.market_data import candle_data
from metatrader.account_info import account_info

def test_mt5_connection():
    """Test MT5 connection and basic functionality"""
    print("=== MT5 Connection Test ===")
    
    # Test 1: Check if MT5 module is available
    print("1. Testing MT5 module import...")
    try:
        print(f"   OK MT5 module imported successfully")
        print(f"   OK MT5 version: {getattr(mt5, '__version__', 'Unknown')}")
    except Exception as e:
        print(f"   ERROR MT5 import failed: {e}")
        return False
    
    # Test 2: Try to initialize MT5
    print("\n2. Testing MT5 initialization...")
    try:
        if mt5.initialize():
            print("   OK MT5 initialized successfully")
            
            # Test 3: Get account info
            print("\n3. Testing account info retrieval...")
            acct_info = account_info()
            if acct_info.get("success"):
                print(f"   OK Account info retrieved successfully")
                print(f"   OK Account: {acct_info.get('login')}")
                print(f"   OK Balance: {acct_info.get('balance')}")
                print(f"   OK Equity: {acct_info.get('equity')}")
                print(f"   OK Currency: {acct_info.get('currency')}")
            else:
                print(f"   ERROR Account info failed: {acct_info.get('error')}")
            
            # Test 4: Test market data access
            print("\n4. Testing market data access...")
            for symbol in config.SYMBOLS[:3]:  # Test first 3 symbols
                print(f"   Testing {symbol}...")
                try:
                    data = candle_data(symbol, "M1", 0, 100)
                    if data:
                        print(f"     OK {symbol} data retrieved: {len(data)} candles")
                    else:
                        print(f"     ERROR {symbol} data failed: No data returned")
                except Exception as e:
                    print(f"     ERROR {symbol} data error: {e}")
            
            # Shutdown MT5
            mt5.shutdown()
            print("\n   OK MT5 shutdown completed")
            return True
        else:
            print(f"   ERROR MT5 initialization failed: {mt5.last_error()}")
            return False
    except Exception as e:
        print(f"   ERROR MT5 initialization error: {e}")
        return False

def test_environment_config():
    """Test environment configuration"""
    print("\n=== Environment Configuration Test ===")
    print(f"1. Login: {config.LOGIN}")
    print(f"2. Server: {config.SERVER}")
    print(f"3. Symbols: {config.SYMBOLS}")
    print(f"4. Magic Number: {config.MAGIC_NUMBER}")
    print(f"5. App Name: {config.APP_NAME}")
    print(f"6. App Env: {config.APP_ENV}")

if __name__ == "__main__":
    test_environment_config()
    test_mt5_connection()