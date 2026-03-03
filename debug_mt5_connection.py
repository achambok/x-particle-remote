#!/usr/bin/env python3
"""
Comprehensive MT5 Connection Debugging Script
This script will analyze the current MT5 connection status and identify the exact issue
"""

import MetaTrader5 as mt5
import time
import os
import subprocess
from config.environments import config

def debug_mt5_connection():
    print("=== MT5 Connection Debugging Script ===")
    print("Analyzing current MT5 connection status...")
    
    # Step 1: Check if MT5 is installed and accessible
    print("\n1. Checking MT5 installation...")
    try:
        mt5.initialize()
        print("OK MT5 library initialized successfully")
    except Exception as e:
        print(f"ERROR: MT5 initialization failed: {e}")
        return
    
    # Step 2: Check terminal info
    print("\n2. Checking terminal information...")
    terminal_info = mt5.terminal_info()
    
    if terminal_info:
        print("OK Terminal information retrieved successfully")
        print(f"   Name: {terminal_info.name}")
        print(f"   Server: {terminal_info.server}")
        print(f"   Login: {terminal_info.login}")
        print(f"   Connected: {terminal_info.connected}")
        print(f"   Demo: {terminal_info.demo}")
    else:
        print("ERROR: Terminal information not available")
    
    # Step 3: Check account info
    print("\n3. Checking account information...")
    account_info = mt5.account_info()
    
    if account_info:
        print("OK Account information retrieved successfully")
        print(f"   Login: {account_info.login}")
        print(f"   Balance: {account_info.balance} {account_info.currency}")
        print(f"   Equity: {account_info.equity}")
        print(f"   Leverage: {account_info.leverage}")
        print(f"   Trade Allowed: {account_info.trade_allowed}")
        print(f"   Trade Mode: {account_info.trade_mode}")
    else:
        print("ERROR: Account information not available")
    
    # Step 4: Check if we can connect to the terminal
    print("\n4. Testing terminal connection...")
    try:
        # Try to get terminal info again
        terminal_info = mt5.terminal_info()
        
        if terminal_info and terminal_info.connected:
            print("OK Terminal is connected")
        else:
            print("ERROR: Terminal is not connected")
            print("   Possible causes:")
            print("   1. MT5 terminal is not running")
            print("   2. MT5 terminal is running but not connected to account")
            print("   3. Python MT5 API is connecting to different terminal instance")
            print("   4. Account credentials are incorrect")
            print("   5. Server is not accessible")
    except Exception as e:
        print(f"ERROR: Error checking terminal connection: {e}")
    
    # Step 5: Check if we can access symbols
    print("\n5. Checking symbol access...")
    symbol = config.FIRST_PAIR
    symbol_info = mt5.symbol_info(symbol)
    
    if symbol_info:
        print(f"OK Symbol {symbol} is accessible")
        print(f"   Point: {symbol_info.point}")
        print(f"   Trade Mode: {symbol_info.trade_mode}")
        print(f"   Volume Min: {symbol_info.volume_min}")
        print(f"   Volume Max: {symbol_info.volume_max}")
        print(f"   Volume Step: {symbol_info.volume_step}")
    else:
        print(f"ERROR: Symbol {symbol} not accessible")
        print("   Possible causes:")
        print("   1. Symbol does not exist")
        print("   2. Terminal is not connected")
        print("   3. Market data is not available")
    
    # Step 6: Check if we can get market data
    print("\n6. Checking market data access...")
    try:
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 5)
        
        if rates is not None and len(rates) > 0:
            print(f"OK Market data accessible: {len(rates)} candles")
            latest = rates[-1]
            print(f"   Latest close: {latest.close}")
            print(f"   Latest time: {latest.time}")
        else:
            print("ERROR: Market data not accessible")
            print("   Possible causes:")
            print("   1. Terminal not connected")
            print("   2. Market data not available")
            print("   3. Symbol not accessible")
    except Exception as e:
        print(f"ERROR: Error accessing market data: {e}")
    
    # Step 7: Check if we can place a test order
    print("\n7. Testing order placement capability...")
    try:
        # Try to get symbol info for trading
        symbol_info = mt5.symbol_info(symbol)
        
        if symbol_info and symbol_info.select:
            print(f"OK Symbol {symbol} available for trading")
            print(f"   Point: {symbol_info.point}")
            print(f"   Trade mode: {symbol_info.trade_mode}")
            
            # Check if trading is allowed
            account_info = mt5.account_info()
            if account_info and account_info.trade_allowed:
                print("OK Trading is allowed on account")
                
                # Check if we can get current price
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    print(f"OK Current price for {symbol}: {tick.ask}")
                    print("SUCCESS: All checks passed - trading should be possible")
                else:
                    print("ERROR: Cannot get current price")
            else:
                print("ERROR: Trading not allowed on account")
                if account_info:
                    print(f"   Trade Allowed: {account_info.trade_allowed}")
                    print(f"   Trade Mode: {account_info.trade_mode}")
                else:
                    print("   Account info not available")
        else:
            print(f"ERROR: Symbol {symbol} not available for trading")
    except Exception as e:
        print(f"ERROR: Error testing trading capability: {e}")
    
    # Step 8: Final diagnosis
    print("\n=== FINAL DIAGNOSIS ===")
    
    # Check if we have any account information
    if account_info is None:
        print("ERROR: CRITICAL: No account information available")
        print("   This means the MT5 Python API is not connected to your terminal")
        print("   Possible causes:")
        print("   1. MT5 terminal is not running")
        print("   2. MT5 terminal is running but not connected to your account")
        print("   3. Python MT5 API is connecting to different terminal instance")
        print("   4. Account credentials are incorrect")
        print("   5. Server is not accessible")
        print("\nSOLUTION:")
        print("1. Close all MT5 instances")
        print("2. Restart MT5 terminal")
        print("3. Login with your account credentials")
        print("4. Verify connection status shows 'Connected'")
        print("5. Keep terminal open and run the bot")
        return
    
    # Check if terminal is connected
    if terminal_info and not terminal_info.connected:
        print("ERROR: CRITICAL: Terminal is not connected")
        print("   The MT5 terminal is running but not connected to your account")
        print("\nSOLUTION:")
        print("1. Close all MT5 instances")
        print("2. Restart MT5 terminal")
        print("3. Login with your account credentials")
        print("4. Verify connection status shows 'Connected'")
        print("5. Keep terminal open and run the bot")
        return
    
    # Check if trading is allowed
    if account_info and not account_info.trade_allowed:
        print("ERROR: CRITICAL: Trading not allowed on account")
        print("   Your account exists but trading is disabled")
        print("\nPossible causes:")
        print("1. Account is in demo mode but trading is disabled")
        print("2. Account has insufficient funds")
        print("3. Account is restricted by broker")
        print("4. Server is not accessible")
        print("\nSOLUTION:")
        print("1. Check your account balance in MT5 terminal")
        print("2. Verify you have trading permissions")
        print("3. Check if server is accessible")
        print("4. Contact broker if issue persists")
        return
    
    # If we reach here, everything should be working
    print("SUCCESS: ALL CHECKS PASSED")
    print("The MT5 Python API is connected and trading should be possible")
    print("\nIf you're still having issues, try:")
    print("1. Restarting the bot")
    print("2. Checking for any error messages")
    print("3. Verifying your account has sufficient funds")
    print("4. Checking if any trading restrictions apply")

# Run the debug function
if __name__ == "__main__":
    debug_mt5_connection()