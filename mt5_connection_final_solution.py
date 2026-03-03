#!/usr/bin/env python3
"""
FINAL SOLUTION: MT5 Python API Connection Fix
This script provides step-by-step instructions and automated fixes for MT5 connection issues.
"""

import MetaTrader5 as mt5
from config.environments import config
import time
import subprocess
import os

def check_mt5_instances():
    """Check for running MT5 instances"""
    print("=== Checking for MT5 Instances ===")
    
    try:
        # Check for running MT5 processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq terminal64.exe'], 
                              capture_output=True, text=True)
        
        if 'terminal64.exe' in result.stdout:
            print("OK MT5 terminal64.exe is running")
            print("Process list:")
            print(result.stdout)
            return True
        else:
            print("ERROR: No MT5 terminal64.exe instances found")
            return False
    except Exception as e:
        print(f"ERROR: Error checking processes: {e}")
        return False

def kill_mt5_instances():
    """Kill all MT5 instances"""
    print("=== Killing MT5 Instances ===")
    
    try:
        # Kill all MT5 processes
        subprocess.run(['taskkill', '/F', '/IM', 'terminal64.exe'], 
                      capture_output=True, text=True)
        print("OK All MT5 instances killed")
        time.sleep(2)  # Wait for processes to fully terminate
        return True
    except Exception as e:
        print(f"ERROR: Error killing processes: {e}")
        return False

def start_mt5_with_account():
    """Start MT5 with explicit account credentials"""
    print("=== Starting MT5 with Account Credentials ===")
    
    terminal_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    
    if not os.path.exists(terminal_path):
        print(f"ERROR: MT5 terminal not found at: {terminal_path}")
        print("Please check the installation path")
        return False
    
    try:
        # Start MT5 with account credentials
        cmd = [
            terminal_path,
            f'/login:{config.LOGIN}',
            f'/password:{config.PASSWD}',
            f'/server:{config.SERVER}'
        ]
        
        print(f"Starting MT5 with command: {' '.join(cmd)}")
        subprocess.Popen(cmd)
        print("OK MT5 started with account credentials")
        
        # Wait for MT5 to initialize
        print("Waiting 10 seconds for MT5 to initialize...")
        time.sleep(10)
        return True
        
    except Exception as e:
        print(f"ERROR: Error starting MT5: {e}")
        return False

def test_connection():
    """Test MT5 connection"""
    print("=== Testing MT5 Connection ===")
    
    # Shutdown any existing connection
    mt5.shutdown()
    time.sleep(1)
    
    # Initialize MT5
    if not mt5.initialize():
        print(f"ERROR: MT5 initialization failed: {mt5.last_error()}")
        return False
    
    print("OK MT5 initialized successfully")
    
    # Check terminal info
    terminal_info = mt5.terminal_info()
    if terminal_info:
        print(f"OK Terminal connected: {terminal_info.name}")
        print(f"OK Server: {terminal_info.server}")
        print(f"OK Login: {terminal_info.login}")
        print(f"OK Connected: {terminal_info.connected}")
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
        
        if account_info.trade_allowed:
            print("OK Trading permissions enabled")
            return True
        else:
            print("ERROR: Trading not allowed")
    else:
        print("ERROR: Account info not available")
    
    mt5.shutdown()
    return False

def main():
    print("MT5 Python API Connection Fix - FINAL SOLUTION")
    print("=" * 60)
    
    # Step 1: Check current status
    print("\n1. Checking current MT5 status...")
    has_instances = check_mt5_instances()
    
    # Step 2: Kill all instances
    print("\n2. Killing all MT5 instances...")
    if has_instances:
        kill_mt5_instances()
    
    # Step 3: Start MT5 with account credentials
    print("\n3. Starting MT5 with account credentials...")
    if not start_mt5_with_account():
        print("\nERROR: Failed to start MT5 with account credentials")
        print("Please try manual connection:")
        print("1. Open MT5 terminal manually")
        print("2. Login with:")
        print(f"   - Login: {config.LOGIN}")
        print(f"   - Password: {config.PASSWD}")
        print(f"   - Server: {config.SERVER}")
        print("3. Verify connection status shows 'Connected'")
        return
    
    # Step 4: Test connection
    print("\n4. Testing connection...")
    success = test_connection()
    
    if success:
        print("\nSUCCESS: MT5 connection established!")
        print("The bot should now be able to trade.")
        print("\nNext steps:")
        print("1. Run the main bot: python main.py")
        print("2. Check the logs to verify trading functionality")
    else:
        print("\nERROR: MT5 connection still not working")
        print("\nPlease try these additional steps:")
        print("1. Check if MT5 is properly installed at the specified path")
        print("2. Verify your account credentials are correct")
        print("3. Check if your MT5 terminal shows 'Connected' status")
        print("4. Try running this script as Administrator")
        print("5. Contact your broker if the issue persists")

if __name__ == "__main__":
    main()