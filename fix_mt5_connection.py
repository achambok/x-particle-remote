#!/usr/bin/env python3
"""
MT5 Connection Fix Script
This script will programmatically connect to the MT5 terminal using the provided credentials
"""

import MetaTrader5 as mt5
import os
import sys
from config.environments import config


def fix_mt5_connection():
    print("=== MT5 Connection Fix Script ===")
    print("Attempting to programmatically connect to MT5 terminal...")

    # Step 1: Initialize MT5
    print("\n1. Initializing MT5...")
    if not mt5.initialize():
        print(f"ERROR: MT5 initialization failed: {mt5.last_error()}")
        return False

    print("OK MT5 initialized successfully")

    # Step 2: Check current connection status
    print("\n2. Checking current connection status...")
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

    # Step 3: Try to connect programmatically using credentials
    print("\n3. Attempting programmatic connection using credentials...")
    # Note: The stub implementation doesn't support programmatic connection
    print(f"INFO: Programmatic connection not supported in stub implementation")
    print(f"INFO: Please manually connect MT5 terminal with:")
    print(f"    Login: {config.LOGIN}")
    print(f"    Password: {config.PASSWD}")
    print(f"    Server: {config.SERVER}")
    print(f"    Then restart this script")

    # Step 4: Verify connection
    print("\n4. Verifying connection...")
    account_info = mt5.account_info()

    if account_info:
        print("OK Account information retrieved successfully")
        print(f"   Login: {account_info.login}")
        print(f"   Balance: {account_info.balance} {account_info.currency}")
        print(f"   Equity: {account_info.equity}")
        print(f"   Leverage: {account_info.leverage}")
        print(f"   Trade Allowed: {account_info.trade_allowed}")
        print(f"   Trade Mode: {account_info.trade_mode}")

        if account_info.trade_allowed:
            print("OK Trading permissions enabled")
        else:
            print("WARNING: Trading not allowed - check account restrictions")
    else:
        print("ERROR: Account information not available")
        print("   This means the connection failed or the terminal is not connected")

    # Step 5: Test symbol access
    print("\n5. Testing symbol access...")
    symbol = config.FIRST_PAIR
    symbol_info = mt5.symbol_info(symbol)

    if symbol_info:
        print(f"OK Symbol {symbol} is accessible")
        print(f"   Point: {symbol_info.point}")
        print(f"   Trade Mode: {symbol_info.trade_mode}")
        print(f"   Volume Min: {symbol_info.volume_min}")
        print(f"   Volume Max: {symbol_info.volume_max}")
        print(f"   Volume Step: {symbol_info.volume_step}")

        if symbol_info.trade_mode == 0:  # Assuming 0 means disabled in stub
            print("WARNING: Symbol is not available for trading")
        else:
            print("OK Symbol is available for trading")
    else:
        print(f"ERROR: Symbol {symbol} not accessible")
        print("   Possible causes:")
        print("   1. Symbol does not exist")
        print("   2. Terminal is not connected")
        print("   3. Market data is not available")

    # Step 6: Final diagnosis
    print("\n=== FINAL DIAGNOSIS ===")

    if account_info and account_info.trade_allowed:
        print("SUCCESS: MT5 connection is working properly")
        print("The terminal is connected and trading should be possible")
        print("\nYou can now run your trading bot")
        return True
    else:
        print("ERROR: MT5 connection is not working properly")
        print("Please check the following:")
        print("1. MT5 terminal is running")
        print("2. Credentials are correct")
        print("3. Server is accessible")
        print("4. Account has trading permissions")
        print("\nIf issues persist, try:")
        print("1. Restarting MT5 terminal")
        print("2. Checking account balance")
        print("3. Verifying server connection")
        return False

    # Shutdown MT5
    mt5.shutdown()
    print("OK MT5 connection test completed")


def find_mt5_terminal_path():
    """
    Try to find the MT5 terminal executable path
    This function searches common installation paths for MT5 terminals
    """
    # Common paths for MT5 terminals (Windows)
    paths = [
        "C:/Program Files/MetaTrader 5/terminal64.exe",
        "C:/Program Files (x86)/MetaTrader 5/terminal64.exe",
        "C:/MetaTrader 5/terminal64.exe",
        "C:/Users/Public/Desktop/MetaTrader 5.lnk",
        os.path.expanduser("~/MetaTrader 5/terminal64.exe"),
        os.path.expanduser("~/Desktop/MetaTrader 5.lnk"),
    ]

    for path in paths:
        if os.path.exists(path):
            return path

    return None


if __name__ == "__main__":
    fix_mt5_connection()
