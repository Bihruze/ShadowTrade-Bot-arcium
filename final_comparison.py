"""
Final Strategy Comparison
Compare all tested strategies
"""

import pandas as pd
from tabulate import tabulate

# Results from all tests
strategies = [
    {
        'Strategy': 'Buy & Hold (Benchmark)',
        'Return %': -31.34,
        'Win Rate %': 100,  # Only 1 trade
        'Total Trades': 1,
        'Profit Factor': 0.0,
        'Max Drawdown %': -31.34,
        'Sharpe Ratio': 0.0,
    },
    {
        'Strategy': 'RSI (30/70)',
        'Return %': -31.26,
        'Win Rate %': 52.1,
        'Total Trades': 48,
        'Profit Factor': 0.73,
        'Max Drawdown %': -129.64,
        'Sharpe Ratio': 1.39,
    },
    {
        'Strategy': 'RSI Optimized (20/80)',
        'Return %': -0.08,
        'Win Rate %': 61.1,
        'Total Trades': 18,
        'Profit Factor': 0.99,
        'Max Drawdown %': -138.16,
        'Sharpe Ratio': 1.47,
    },
    {
        'Strategy': 'RSI + Trend Filter',
        'Return %': -26.16,
        'Win Rate %': 45.0,
        'Total Trades': 20,
        'Profit Factor': 0.45,
        'Max Drawdown %': -114.86,
        'Sharpe Ratio': 0.21,
    },
    {
        'Strategy': 'MA Crossover (7/25)',
        'Return %': -28.88,
        'Win Rate %': 29.3,
        'Total Trades': 99,
        'Profit Factor': 0.88,
        'Max Drawdown %': -104.20,
        'Sharpe Ratio': 1.11,
    },
    {
        'Strategy': 'MACD Crossover',
        'Return %': -65.89,
        'Win Rate %': 33.1,
        'Total Trades': 181,
        'Profit Factor': 0.72,
        'Max Drawdown %': -104.04,
        'Sharpe Ratio': -3.81,
    },
]

# Convert to DataFrame
df = pd.DataFrame(strategies)

# Sort by return
df_sorted = df.sort_values('Return %', ascending=False).reset_index(drop=True)

# Add rank
df_sorted.insert(0, 'Rank', range(1, len(df_sorted) + 1))

print("\n" + "="*100)
print("🏆 FINAL STRATEGY COMPARISON - SOL/USDT (6 Months)")
print("="*100)
print()

# Print table
print(tabulate(df_sorted, headers='keys', tablefmt='grid', floatfmt='.2f', showindex=False))

print("\n" + "="*100)
print("📊 KEY INSIGHTS")
print("="*100)

print("\n🥇 WINNER: RSI Optimized (20/80)")
print("   • Almost break-even in downtrend market (-0.08%)")
print("   • Highest win rate (61.1%)")
print("   • Fewest trades (18) - selective")
print("   • Best risk-adjusted returns (Sharpe: 1.47)")

print("\n🥈 RUNNER-UP: RSI + Trend Filter")
print("   • Better than buy & hold (-26.16% vs -31.34%)")
print("   • Avoided some losing trades")
print("   • But still couldn't profit in downtrend")

print("\n❌ WORST: MACD Crossover")
print("   • Overtrading (181 trades)")
print("   • Low win rate (33.1%)")
print("   • Commissions ate profits")
print("   • Sharpe ratio negative!")

print("\n💡 CONCLUSIONS:")
print("   1. Market was in DOWNTREND (-31% drop)")
print("   2. ALL strategies lost money (bearish market)")
print("   3. RSI (20/80) was BEST at preserving capital")
print("   4. Mean-reversion beats trend-following in choppy markets")
print("   5. Overtrading kills returns (MACD = -65%!)")

print("\n🚀 RECOMMENDATIONS FOR PRODUCTION:")
print("   1. Use RSI (20/80) with extreme thresholds")
print("   2. Add market regime filter (bull vs bear)")
print("   3. Consider SHORT positions in downtrends")
print("   4. Combine multiple strategies (ensemble)")
print("   5. Add volatility-based position sizing")
print("   6. Test on MULTIPLE timeframes (1h, 4h, 1d)")

print("\n⚠️  IMPORTANT:")
print("   • These results are from ONE 6-month period")
print("   • Need to test on different market conditions")
print("   • Walk-forward optimization required")
print("   • Paper trade before going live!")

print("\n" + "="*100)

