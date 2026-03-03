#!/usr/bin/env python3
"""
Script to connect MT5 terminal to demo account programmatically
"""

import MetaTrader5 as mt5
from config.environments import config

def connect_mt5_account():
    print("=== MT5 Account Connection Script ===")
    
    # Initialize MT5 if not already initialized
    if not mt5.initialize():
        print(f"ERROR: MT5 initialization failed: {mt5.last_error()}")
        return False
    
    print("OK MT5 initialized successfully")
    
    # Attempt to connect to the demo account
    print(f"Attempting to connect to account {config.LOGIN}...")
    
    # Note: MT5.connect() typically connects to the terminal that's already running
    # If the terminal is not connected to the account, this won't work
    # The terminal needs to be connected manually first
    
    # Check if we can get account info (this will only work if terminal is connected)
    account_info = mt5.account_info()
    
    if account_info is None:
        print("ERROR: Account not connected. Please manually connect the MT5 terminal:")
        print(f"   1. Open MT5 terminal")
        print(f"   2. File → Login to Trade Account")
        print(f"   3. Login: {config.LOGIN}")
        print(f"   4. Password: {config.PASSWD}")
        print(f"   5. Server: {config.SERVER}")
        print(f"   6. Click Login")
        print(f"   7. Verify status shows 'Connected'")
        print(f"   8. Restart this bot after connection")
        return False
    
    # If we get here, the account is connected
    print(f"OK Account connected successfully!")
    print(f"   Account: {account_info.login}")
    print(f"   Balance: {account_info.balance} {account_info.currency}")
    print(f"   Equity: {account_info.equity}")
    print(f"   Leverage: {account_info.leverage}")
    print(f"   Trade Allowed: {account_info.trade_allowed}")
    
    # Test trading permissions
    if account_info.trade_allowed:
        print("OK Trading permissions enabled")
    else:
        print("ERROR: Trading not allowed - check account restrictions")
    
    # Shutdown MT5
    mt5.shutdown()
    print("OK MT5 connection test completed")
    
    return True

if __name__ == "__main__":
    connect_mt5_account()