"""
Buy and Hold Strategy (Benchmark)
Simply buy at start and hold until end
"""

import pandas as pd
from data_fetcher import DataFetcher

# Load data
print("📥 Loading data...")
fetcher = DataFetcher()
df = fetcher.load_from_csv("SOLUSDT_1h_2024-04-01_to_2024-10-04.csv")

# Calculate buy and hold
initial_capital = 10000
start_price = df.iloc[0]['close']
end_price = df.iloc[-1]['close']

# How many tokens we can buy
tokens = initial_capital / start_price

# Final value
final_value = tokens * end_price

# Return
return_pct = ((final_value - initial_capital) / initial_capital) * 100

print("\n" + "="*60)
print("📊 BUY & HOLD BENCHMARK")
print("="*60)
print(f"\n💰 Capital:")
print(f"   Initial: ${initial_capital:,.2f}")
print(f"   Final:   ${final_value:,.2f}")
print(f"   P&L:     ${final_value - initial_capital:,.2f}")

color = "🟢" if return_pct > 0 else "🔴"
print(f"   Return:  {color} {return_pct:.2f}%")

print(f"\n📈 Trade:")
print(f"   Entry Price: ${start_price:.2f}")
print(f"   Exit Price:  ${end_price:.2f}")
print(f"   Price Change: {((end_price - start_price) / start_price * 100):.2f}%")
print(f"   Tokens Held: {tokens:.4f} SOL")

print(f"\n📅 Period:")
print(f"   Start: {df.index[0]}")
print(f"   End:   {df.index[-1]}")
print(f"   Duration: {(df.index[-1] - df.index[0]).days} days")

print("\n" + "="*60)

