"""
RSI + Trend Filter Strategy
Only buy when price is above 200 EMA (uptrend)
"""

from backtest_engine import BacktestEngine
import pandas as pd
from typing import Dict


class RSITrendStrategy(BacktestEngine):
    """RSI strategy with trend filter"""
    
    def run_rsi_with_trend(
        self,
        df: pd.DataFrame,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        trend_period: int = 200,
    ) -> Dict:
        """
        RSI strategy with EMA trend filter
        
        Rules:
        - Only BUY when RSI < oversold AND price > 200 EMA (uptrend)
        - SELL when RSI > overbought
        """
        self.reset()
        
        rsi_col = f'RSI_{rsi_period}'
        trend_col = f'EMA_{trend_period}' if f'EMA_{trend_period}' in df.columns else 'SMA_200'
        
        print(f"\n🚀 Running RSI + Trend Filter Strategy...")
        print(f"   RSI: Buy < {rsi_oversold}, Sell > {rsi_overbought}")
        print(f"   Trend Filter: Only buy when price > {trend_col}")
        print(f"   Initial Capital: ${self.initial_capital:,.2f}")
        print()
        
        for i, (timestamp, row) in enumerate(df.iterrows()):
            price = row['close']
            rsi = row[rsi_col]
            trend = row.get(trend_col, 0)
            
            if pd.isna(rsi) or pd.isna(trend):
                continue
            
            # Check if in uptrend
            in_uptrend = price > trend
            
            # Trading logic
            if not self.position or not self.position.is_open:
                # BUY: RSI oversold AND uptrend
                if rsi < rsi_oversold and in_uptrend:
                    self.buy(timestamp, price)
            else:
                # SELL: RSI overbought
                if rsi > rsi_overbought:
                    self.sell(timestamp, price)
            
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
    engine = RSITrendStrategy(initial_capital=10000, commission=0.1)
    results = engine.run_rsi_with_trend(df)
    
    if results:
        engine.print_results(results)

