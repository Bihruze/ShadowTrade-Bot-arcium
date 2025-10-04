"""
Moving Average Crossover Strategy
BUY when fast EMA crosses above slow EMA
SELL when fast EMA crosses below slow EMA
"""

from backtest_engine import BacktestEngine
import pandas as pd
from typing import Dict


class MACrossStrategy(BacktestEngine):
    """Moving Average crossover strategy"""
    
    def run_ma_cross_strategy(
        self,
        df: pd.DataFrame,
        fast_period: int = 7,
        slow_period: int = 25,
    ) -> Dict:
        """
        MA crossover strategy (Golden/Death Cross)
        
        Rules:
        - BUY when fast MA crosses above slow MA (golden cross)
        - SELL when fast MA crosses below slow MA (death cross)
        """
        self.reset()
        
        fast_col = f'EMA_{fast_period}'
        slow_col = f'EMA_{slow_period}'
        
        print(f"\n🚀 Running MA Crossover Strategy...")
        print(f"   Fast: {fast_col}, Slow: {slow_col}")
        print(f"   Initial Capital: ${self.initial_capital:,.2f}")
        print()
        
        prev_fast = None
        prev_slow = None
        
        for i, (timestamp, row) in enumerate(df.iterrows()):
            price = row['close']
            fast = row[fast_col]
            slow = row[slow_col]
            
            if pd.isna(fast) or pd.isna(slow):
                continue
            
            # Detect crossovers
            if prev_fast is not None and prev_slow is not None:
                # Golden cross: fast crosses above slow
                golden_cross = prev_fast <= prev_slow and fast > slow
                
                # Death cross: fast crosses below slow
                death_cross = prev_fast >= prev_slow and fast < slow
                
                # Trading logic
                if not self.position or not self.position.is_open:
                    if golden_cross:
                        self.buy(timestamp, price)
                else:
                    if death_cross:
                        self.sell(timestamp, price)
            
            prev_fast = fast
            prev_slow = slow
            self.update_equity(timestamp, price)
        
        # Close open position
        if self.position and self.position.is_open:
            self.sell(df.index[-1], df.iloc[-1]['close'])
        
        results = self.calculate_metrics(df)
        return results


if __name__ == "__main__":
    from data_fetcher import DataFetcher
    from indicators import TechnicalIndicators
    
    # Load data
    print("📥 Loading data...")
    fetcher = DataFetcher()
    df = fetcher.load_from_csv("SOLUSDT_1h_2024-04-01_to_2024-10-04.csv")
    
    # Calculate indicators
    print("📊 Calculating indicators...")
    df = TechnicalIndicators.add_all_indicators(df)
    
    # Run strategy
    engine = MACrossStrategy(initial_capital=10000, commission=0.1)
    results = engine.run_ma_cross_strategy(df, fast_period=7, slow_period=25)
    
    if results:
        engine.print_results(results)

