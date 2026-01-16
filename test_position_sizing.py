print('='*60)
print('X-PARTICLE POSITION SIZING TEST')
print('='*60)
print()

from metatrader.indicators import calculate_position_size

# Test the new position sizing vs old broken system
balance = 500
risk_pct = 4.0
sl_pips = 25.0
symbol = 'EURUSDm'

result = calculate_position_size(balance, risk_pct, sl_pips, symbol)

print(f'Account Balance: ${balance}')
print(f'Risk Percentage: {risk_pct}%')
print(f'Stop Loss: {sl_pips} pips')
print()
print('NEW SYSTEM (After Fix):')
print(f'  Recommended Volume: {result["volume"]} lots')
print(f'  Risk Amount: ${result["risk_amount"]:.2f}')
print(f'  Pip Value: ${result["pip_value"]:.2f}')
print()
print('OLD SYSTEM (Before Fix):')
print(f'  Hardcoded Volume: 0.02 lots')
print(f'  Actual Risk: $5.00 (1% - WRONG!)')
print()
print('='*60)
print(f'IMPROVEMENT: {result["volume"] / 0.02:.1f}x more effective position size')
print('='*60)
