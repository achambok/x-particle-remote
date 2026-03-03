#!/usr/bin/env python3
"""
Script to find the correct Exness MT5 terminal path
"""

import os
import subprocess

def find_mt5_terminal():
    """Find MT5 terminal executable"""
    print("=== Finding MT5 Terminal ===")
    
    # Common MT5 installation paths
    common_paths = [
        r"C:\Program Files\Exness\terminal64.exe",
        r"C:\Program Files (x86)\Exness\terminal64.exe",
        r"C:\Program Files\Exness MT5\terminal64.exe",
        r"C:\Program Files (x86)\Exness MT5\terminal64.exe",
        r"C:\Program Files\Exness MT5 Trial\terminal64.exe",
        r"C:\Program Files (x86)\Exness MT5 Trial\terminal64.exe",
        r"C:\Program Files\MetaTrader 5\terminal64.exe",
        r"C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
    ]
    
    found_paths = []
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"OK Found MT5 terminal at: {path}")
            found_paths.append(path)
        else:
            print(f"ERROR: Not found: {path}")
    
    if not found_paths:
        print("\nERROR: No MT5 terminal found in common paths")
        print("Please check your Exness MT5 installation")
        
        # Try to find any terminal64.exe
        print("\nSearching for any terminal64.exe files...")
        try:
            result = subprocess.run(['dir', '/s', 'terminal64.exe'], 
                                  capture_output=True, text=True, shell=True)
            if result.stdout:
                print("Found terminal64.exe files:")
                print(result.stdout)
            else:
                print("No terminal64.exe files found")
        except Exception as e:
            print(f"Error searching: {e}")
        
        return None
    
    return found_paths[0]  # Return the first found path

def main():
    print("Exness MT5 Terminal Path Finder")
    print("=" * 40)
    
    path = find_mt5_terminal()
    
    if path:
        print(f"\nSUCCESS: Recommended path: {path}")
        print("\nTo use this path, update the terminal_path variable in mt5_connection_final_solution.py")
    else:
        print("\nERROR: Could not find MT5 terminal")
        print("Please manually locate your Exness MT5 installation")

if __name__ == "__main__":
    main()