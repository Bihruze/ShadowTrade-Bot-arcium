"""
MACD Crossover Strategy
BUY when MACD crosses above Signal
SELL when MACD crosses below Signal
"""

from backtest_engine import BacktestEngine
import pandas as pd
from typing import Dict


class MACDStrategy(BacktestEngine):
    """MACD crossover strategy"""
    
    def run_macd_strategy(
        self,
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> Dict:
        """
        MACD crossover strategy
        
        Rules:
        - BUY when MACD crosses above Signal line (bullish crossover)
        - SELL when MACD crosses below Signal line (bearish crossover)
        """
        self.reset()
        
        print(f"\n🚀 Running MACD Crossover Strategy...")
        print(f"   MACD: {fast}/{slow}/{signal}")
        print(f"   Initial Capital: ${self.initial_capital:,.2f}")
        print()
        
        prev_macd = None
        prev_signal = None
        
        for i, (timestamp, row) in enumerate(df.iterrows()):
            price = row['close']
            macd = row['MACD']
            macd_signal = row['MACD_signal']
            
            if pd.isna(macd) or pd.isna(macd_signal):
                continue
            
            # Detect crossovers
            if prev_macd is not None and prev_signal is not None:
                # Bullish crossover: MACD crosses above Signal
                bullish_cross = prev_macd <= prev_signal and macd > macd_signal
                
                # Bearish crossover: MACD crosses below Signal
                bearish_cross = prev_macd >= prev_signal and macd < macd_signal
                
                # Trading logic
                if not self.position or not self.position.is_open:
                    if bullish_cross:
                        self.buy(timestamp, price)
                else:
                    if bearish_cross:
                        self.sell(timestamp, price)
            
            prev_macd = macd
            prev_signal = macd_signal
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
    engine = MACDStrategy(initial_capital=10000, commission=0.1)
    results = engine.run_macd_strategy(df)
    
    if results:
        engine.print_results(results)

