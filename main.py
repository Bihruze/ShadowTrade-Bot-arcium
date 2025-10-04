"""
Main Runner - RSI Strategy Backtest
Runs complete backtest pipeline
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from data_fetcher import DataFetcher
from indicators import TechnicalIndicators
from backtest_engine import BacktestEngine
from visualizer import Visualizer


def run_rsi_backtest(
    symbol: str = "SOLUSDT",
    interval: str = "1h",
    start_date: str = "2024-04-01",
    end_date: str = "2024-10-04",
    
    # Strategy parameters
    rsi_period: int = 14,
    rsi_oversold: float = 30,
    rsi_overbought: float = 70,
    
    # Risk management
    stop_loss_pct: float = None,
    take_profit_pct: float = None,
    
    # Backtest settings
    initial_capital: float = 10000,
    position_size_pct: float = 100,
    commission: float = 0.1,
    slippage: float = 0.05,
    
    # Output
    save_data: bool = True,
    save_charts: bool = True,
):
    """
    Run complete RSI backtest
    
    Args:
        symbol: Trading pair (e.g., SOLUSDT)
        interval: Timeframe (1h, 4h, 1d)
        start_date: Start date YYYY-MM-DD
        end_date: End date YYYY-MM-DD
        rsi_period: RSI calculation period
        rsi_oversold: Buy signal threshold
        rsi_overbought: Sell signal threshold
        stop_loss_pct: Stop loss percentage (optional)
        take_profit_pct: Take profit percentage (optional)
        initial_capital: Starting capital
        position_size_pct: Position size as % of capital
        commission: Commission per trade (%)
        slippage: Slippage per trade (%)
        save_data: Save historical data to CSV
        save_charts: Save charts to PNG
    """
    
    print("=" * 70)
    print("🤖 RSI STRATEGY BACKTEST")
    print("=" * 70)
    
    # Step 1: Fetch data
    print("\n📥 Step 1: Fetching historical data...")
    fetcher = DataFetcher()
    
    try:
        df = fetcher.fetch_binance_data(
            symbol=symbol,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return
    
    if save_data:
        filename = f"{symbol}_{interval}_{start_date}_to_{end_date}.csv"
        fetcher.save_to_csv(df, filename)
    
    # Step 2: Calculate indicators
    print("\n📊 Step 2: Calculating technical indicators...")
    df = TechnicalIndicators.add_all_indicators(df)
    
    # Step 3: Run backtest
    print("\n🔄 Step 3: Running backtest...")
    engine = BacktestEngine(
        initial_capital=initial_capital,
        position_size_pct=position_size_pct,
        commission=commission,
        slippage=slippage,
    )
    
    results = engine.run_rsi_strategy(
        df=df,
        rsi_period=rsi_period,
        rsi_oversold=rsi_oversold,
        rsi_overbought=rsi_overbought,
        stop_loss_pct=stop_loss_pct,
        take_profit_pct=take_profit_pct,
    )
    
    if not results:
        print("❌ Backtest failed - no trades executed")
        return
    
    # Step 4: Print results
    engine.print_results(results)
    
    # Step 5: Visualize
    print("\n📈 Step 4: Creating visualizations...")
    
    if save_charts:
        save_path = f"backtest_{symbol}_{interval}"
        Visualizer.create_dashboard(df, results, save_path=save_path)
    else:
        Visualizer.create_dashboard(df, results)
    
    print("\n✅ Backtest complete!")
    
    return df, results


def compare_parameters():
    """
    Compare different RSI parameters
    Finds optimal oversold/overbought levels
    """
    
    print("\n" + "=" * 70)
    print("🔬 RSI PARAMETER OPTIMIZATION")
    print("=" * 70)
    
    # Fetch data once
    print("\n📥 Fetching data...")
    fetcher = DataFetcher()
    df = fetcher.fetch_binance_data(
        symbol="SOLUSDT",
        interval="1h",
        start_date="2024-04-01",
        end_date="2024-10-04",
    )
    
    df = TechnicalIndicators.add_all_indicators(df)
    
    # Test different parameters
    oversold_levels = [20, 25, 30, 35]
    overbought_levels = [65, 70, 75, 80]
    
    results_comparison = []
    
    print("\n🔄 Testing parameter combinations...")
    
    for oversold in oversold_levels:
        for overbought in overbought_levels:
            print(f"\n   Testing: RSI < {oversold} / RSI > {overbought}")
            
            engine = BacktestEngine(initial_capital=10000, commission=0.1)
            results = engine.run_rsi_strategy(
                df=df,
                rsi_oversold=oversold,
                rsi_overbought=overbought,
            )
            
            if results and results['total_trades'] > 0:
                results_comparison.append({
                    'oversold': oversold,
                    'overbought': overbought,
                    'return_pct': results['total_return_pct'],
                    'total_trades': results['total_trades'],
                    'win_rate': results['win_rate'],
                    'sharpe_ratio': results['sharpe_ratio'],
                    'max_drawdown': results['max_drawdown'],
                })
    
    # Display results
    print("\n" + "=" * 70)
    print("📊 PARAMETER COMPARISON RESULTS")
    print("=" * 70)
    
    comparison_df = pd.DataFrame(results_comparison)
    comparison_df = comparison_df.sort_values('return_pct', ascending=False)
    
    print("\nTop 5 Parameter Combinations:")
    print(comparison_df.head(10).to_string(index=False))
    
    # Best parameters
    best = comparison_df.iloc[0]
    print(f"\n🏆 BEST PARAMETERS:")
    print(f"   RSI Oversold:  {best['oversold']}")
    print(f"   RSI Overbought: {best['overbought']}")
    print(f"   Return:        {best['return_pct']:.2f}%")
    print(f"   Win Rate:      {best['win_rate']:.1f}%")
    print(f"   Sharpe Ratio:  {best['sharpe_ratio']:.2f}")
    
    return comparison_df


def quick_test():
    """Quick test with default parameters"""
    
    return run_rsi_backtest(
        symbol="SOLUSDT",
        interval="1h",
        start_date="2024-04-01",
        end_date="2024-10-04",
        rsi_oversold=30,
        rsi_overbought=70,
        initial_capital=10000,
        save_data=True,
        save_charts=True,
    )


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("🚀 RSI STRATEGY BACKTEST TOOL")
    print("="*70)
    print("\nOptions:")
    print("1. Run default backtest")
    print("2. Run parameter optimization")
    print("3. Run custom backtest")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        print("\n▶️  Running default backtest...")
        quick_test()
        
    elif choice == "2":
        print("\n▶️  Running parameter optimization...")
        compare_parameters()
        
    elif choice == "3":
        print("\n▶️  Custom backtest configuration:")
        
        symbol = input("Symbol (default SOLUSDT): ").strip() or "SOLUSDT"
        interval = input("Interval (1h/4h/1d, default 1h): ").strip() or "1h"
        
        print("\nFetching available data...")
        print("(Press Enter to use defaults)")
        
        start_date = input("Start date (YYYY-MM-DD, default 2024-04-01): ").strip() or "2024-04-01"
        end_date = input("End date (YYYY-MM-DD, default 2024-10-04): ").strip() or "2024-10-04"
        
        rsi_oversold = float(input("RSI Oversold level (default 30): ").strip() or "30")
        rsi_overbought = float(input("RSI Overbought level (default 70): ").strip() or "70")
        
        use_sl = input("Use stop loss? (y/n, default n): ").strip().lower() == 'y'
        stop_loss = float(input("Stop loss % (default 5): ").strip() or "5") if use_sl else None
        
        use_tp = input("Use take profit? (y/n, default n): ").strip().lower() == 'y'
        take_profit = float(input("Take profit % (default 15): ").strip() or "15") if use_tp else None
        
        initial_capital = float(input("Initial capital (default 10000): ").strip() or "10000")
        
        print("\n▶️  Running custom backtest...")
        run_rsi_backtest(
            symbol=symbol,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            rsi_oversold=rsi_oversold,
            rsi_overbought=rsi_overbought,
            stop_loss_pct=stop_loss,
            take_profit_pct=take_profit,
            initial_capital=initial_capital,
            save_data=True,
            save_charts=True,
        )
    
    else:
        print("❌ Invalid choice. Running default backtest...")
        quick_test()
    
    print("\n👋 Done! Check the generated charts and CSV files.")

