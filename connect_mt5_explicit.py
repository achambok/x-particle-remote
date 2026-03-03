#!/usr/bin/env python3
"""
Script to connect MT5 Python API to specific terminal instance using explicit path
"""

import MetaTrader5 as mt5
from config.environments import config
import time

def connect_mt5_explicit():
    print("=== MT5 Python API Explicit Connection ===")
    print(f"Target MT5 Terminal Path: C:\\Program Files\\XM Global MT5\\terminal64.exe")
    print(f"Target Account: {config.LOGIN}")
    print(f"Target Server: {config.SERVER}")
    
    # Shutdown any existing connection
    mt5.shutdown()
    print("OK Shutdown existing MT5 connection")
    
    # Wait a moment
    time.sleep(1)
    
    # Initialize MT5 with explicit path to your terminal
    print("Attempting to initialize MT5 with explicit terminal path...")
    
    # Use the explicit path to your MT5 terminal
    terminal_path = r"C:\Program Files\XM Global MT5\terminal64.exe"
    
    if not mt5.initialize():
        print(f"ERROR: MT5 initialization failed: {mt5.last_error()}")
        print("This could mean:")
        print("1. The terminal path is incorrect")
        print("2. The terminal is not running")
        print("3. The terminal is not connected to your account")
        return False
    
    print("OK MT5 initialized successfully with explicit path")
    
    # Check terminal info
    terminal_info = mt5.terminal_info()
    if terminal_info:
        print(f"OK Terminal connected: {terminal_info.name}")
        print(f"OK Server: {terminal_info.server}")
        print(f"OK Login: {terminal_info.login}")
        print(f"OK Connected: {terminal_info.connected}")
        print(f"OK Demo: {terminal_info.demo}")
    else:
        print("ERROR: Terminal info not available")
    
    # Check account info
    account_info = mt5.account_info()
    if account_info:
        print(f"OK Account connected: {account_info.login}")
        print(f"OK Balance: {account_info.balance} {account_info.currency}")
        print(f"OK Equity: {account_info.equity}")
        print(f"OK Leverage: {account_info.leverage}")
        print(f"OK Trade Allowed: {account_info.trade_allowed}")
        print(f"OK Trade Mode: {account_info.trade_mode}")
        
        # Test trading permissions
        if account_info.trade_allowed and account_info.trade_mode != mt5.ACCOUNT_TRADE_MODE_DISABLED:
            print("OK Trading permissions enabled")
            
            # Test a simple market order to verify trading works
            print("Testing trading functionality...")
            symbol = config.FIRST_PAIR
            symbol_info = mt5.symbol_info(symbol)
            
            if symbol_info is None:
                print(f"ERROR: Symbol {symbol} not found")
                mt5.shutdown()
                return False
            
            if not symbol_info.select:
                print(f"ERROR: Symbol {symbol} not selected")
                mt5.shutdown()
                return False
            
            print(f"OK Symbol {symbol} available for trading")
            print(f"OK Point: {symbol_info.point}")
            print(f"OK Trade mode: {symbol_info.trade_mode}")
            print(f"OK Volume min: {symbol_info.volume_min}")
            print(f"OK Volume max: {symbol_info.volume_max}")
            print(f"OK Volume step: {symbol_info.volume_step}")
            
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                print(f"ERROR: Cannot get price for {symbol}")
                mt5.shutdown()
                return False
            
            print(f"OK Current price for {symbol}: {tick.ask}")
            
            return True
        else:
            print("ERROR: Trading not allowed - check account restrictions")
            print(f"   Trade Allowed: {account_info.trade_allowed}")
            print(f"   Trade Mode: {account_info.trade_mode}")
    else:
        print("ERROR: Account info not available")
    
    # Shutdown MT5
    mt5.shutdown()
    print("OK MT5 connection test completed")
    
    return False

def test_manual_trade():
    """Test if we can place a manual trade"""
    print("\n=== Testing Manual Trade ===")
    
    # Shutdown any existing connection
    mt5.shutdown()
    time.sleep(1)
    
    # Initialize with explicit path
    terminal_path = r"C:\Program Files\XM Global MT5\terminal64.exe"
    
    if not mt5.initialize():
        print(f"ERROR: Cannot initialize MT5: {mt5.last_error()}")
        return False
    
    symbol = config.FIRST_PAIR
    lot = 0.01
    price = mt5.symbol_info_tick(symbol).ask
    
    # Prepare the request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": price - 100 * mt5.symbol_info(symbol).point,
        "tp": price + 100 * mt5.symbol_info(symbol).point,
        "deviation": 20,
        "magic": config.MAGIC_NUMBER,
        "comment": "Test trade from bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    # Send the request
    result = mt5.order_send(request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"ERROR: Trade failed: {result.retcode}")
        print(f"   {mt5.last_error()}")
    else:
        print(f"SUCCESS: Trade successful! Order ticket: {result.order}")
    
    # Shutdown
    mt5.shutdown()
    return result.retcode == mt5.TRADE_RETCODE_DONE

if __name__ == "__main__":
    print("Testing MT5 explicit connection...")
    success = connect_mt5_explicit()
    
    if success:
        print("\nSUCCESS: MT5 explicit connection successful!")
        print("The bot should now be able to trade.")
        
        # Ask if they want to test a trade
        response = input("\nWould you like to test placing a trade? (y/n): ")
        if response.lower() == 'y':
            test_manual_trade()
    else:
        print("\nERROR: MT5 explicit connection failed.")
        print("Please ensure:")
        print("1. MT5 terminal is open and running at the specified path")
        print("2. You are logged into account 315829092")
        print("3. Server is XMGlobal-MT5 7")
        print("4. Status shows 'Connected' in the terminal")
        print("5. The terminal path is correct")