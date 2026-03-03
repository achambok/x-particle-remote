import json
from datetime import datetime
from tools.trade_frequency_tools import get_trading_statistics_tool

def display_dashboard():
    """
    Reads trading statistics and history, then prints a formatted
    dashboard to the console.
    """
    print("=========================================")
    print("   X-Particle Trading Bot Monitor        ")
    print("=========================================")
    print()

    # --- Get and display overall statistics ---
    try:
        stats_json_str = get_trading_statistics_tool.invoke({})
        stats = json.loads(stats_json_str)

        print("--- Overall Statistics (All Time) ---")
        print(f"Total Attempts:      {stats.get('total_attempts', 'N/A')}")
        print(f"Successful Trades:   {stats.get('successful_trades', 'N/A')}")
        print(f"Rejected Trades:     {stats.get('rejected_trades', 'N/A')}")
        print(f"Rejection Rate:      {stats.get('rejection_rate_pct', 'N/A')}%")
        print(f"Avg Trades Per Day:  {stats.get('avg_trades_per_day', 'N/A')}")
        print()

        # --- Display today's activity ---
        today_stats = stats.get('today')
        if today_stats and stats.get('daily_stats'):
            today_str = list(stats.get('daily_stats', {}).keys())[-1] # Get the most recent date
            print(f"--- Today's Activity ({today_str}) ---")
            print(f"Total Attempts:      {today_stats.get('total_attempts', 'N/A')}")
            print(f"Successful Trades:   {today_stats.get('successful_trades', 'N/A')}")
            print(f"Rejected Trades:     {today_stats.get('rejected_trades', 'N/A')}")
            if today_stats.get('last_trade_time'):
                last_time = datetime.fromisoformat(today_stats['last_trade_time']).strftime('%H:%M:%S')
                print(f"Last Activity:       {last_time}")
            print()
        else:
            print("--- No activity recorded today ---")
            print()

    except Exception as e:
        print(f"Could not load statistics: {e}")
        print()

    # --- Get and display recent trade decisions ---
    print("--- Recent Trade Decisions (Last 10) ---")
    try:
        with open('logs/trade_history.json', 'r') as f:
            history = json.load(f)
        
        trades = history.get('trades', [])
        if not trades:
            print("No trade decisions have been logged yet.")
        else:
            # Display the last 10 trades, most recent first
            for trade in reversed(trades[-10:]):
                ts = datetime.fromisoformat(trade['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                decision = "EXECUTED" if trade['success'] else "REJECTED"
                print(f"[{ts}] {decision} ({trade.get('order_type')} {trade.get('symbol')}): {trade.get('reason')}")

    except FileNotFoundError:
        print("Log file 'logs/trade_history.json' not found.")
    except Exception as e:
        print(f"Could not read trade history: {e}")
    
    print("\n=========================================")

if __name__ == "__main__":
    display_dashboard()