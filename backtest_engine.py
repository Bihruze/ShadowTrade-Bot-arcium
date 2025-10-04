"""
Backtest Engine
Simulates trading strategies on historical data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:
    """Represents a single trade"""
    entry_time: datetime
    entry_price: float
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    position_size: float = 1.0
    side: str = "long"  # "long" or "short"
    
    @property
    def is_open(self) -> bool:
        return self.exit_time is None
    
    @property
    def pnl(self) -> float:
        """Calculate profit/loss"""
        if not self.exit_price:
            return 0.0
        
        if self.side == "long":
            return (self.exit_price - self.entry_price) * self.position_size
        else:
            return (self.entry_price - self.exit_price) * self.position_size
    
    @property
    def pnl_percent(self) -> float:
        """Calculate profit/loss percentage"""
        if not self.exit_price:
            return 0.0
        
        if self.side == "long":
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - self.exit_price) / self.entry_price) * 100
    
    @property
    def duration(self) -> Optional[pd.Timedelta]:
        """Calculate trade duration"""
        if not self.exit_time:
            return None
        return self.exit_time - self.entry_time


class BacktestEngine:
    """Backtest trading strategies"""
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        position_size_pct: float = 100.0,  # % of capital per trade
        commission: float = 0.1,  # % commission per trade
        slippage: float = 0.05,  # % slippage
    ):
        self.initial_capital = initial_capital
        self.position_size_pct = position_size_pct
        self.commission = commission / 100
        self.slippage = slippage / 100
        
        # State
        self.capital = initial_capital
        self.position: Optional[Trade] = None
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.timestamps: List[datetime] = []
    
    def reset(self):
        """Reset backtest state"""
        self.capital = self.initial_capital
        self.position = None
        self.trades = []
        self.equity_curve = []
        self.timestamps = []
    
    def buy(self, timestamp: datetime, price: float):
        """Open a long position"""
        if self.position and self.position.is_open:
            return  # Already in position
        
        # Apply slippage (buy at slightly higher price)
        entry_price = price * (1 + self.slippage)
        
        # Calculate position size
        position_value = self.capital * (self.position_size_pct / 100)
        commission_cost = position_value * self.commission
        available_for_position = position_value - commission_cost
        position_size = available_for_position / entry_price
        
        # Create trade
        self.position = Trade(
            entry_time=timestamp,
            entry_price=entry_price,
            position_size=position_size,
            side="long"
        )
        
        # Update capital (deduct full position value + commission)
        self.capital -= position_value
    
    def sell(self, timestamp: datetime, price: float):
        """Close a long position"""
        if not self.position or not self.position.is_open:
            return  # No open position
        
        # Apply slippage (sell at slightly lower price)
        exit_price = price * (1 - self.slippage)
        
        # Close position
        self.position.exit_time = timestamp
        self.position.exit_price = exit_price
        
        # Calculate proceeds (gross value from selling position)
        gross_proceeds = self.position.position_size * exit_price
        commission_cost = gross_proceeds * self.commission
        net_proceeds = gross_proceeds - commission_cost
        
        # Update capital (add back net proceeds)
        self.capital += net_proceeds
        
        # Save trade
        self.trades.append(self.position)
        self.position = None
    
    def update_equity(self, timestamp: datetime, current_price: float):
        """Update equity curve"""
        equity = self.capital
        
        # Add unrealized PnL if in position
        if self.position and self.position.is_open:
            unrealized_value = self.position.position_size * current_price
            cost_basis = self.position.position_size * self.position.entry_price
            equity += (unrealized_value - cost_basis)
        
        # Prevent overflow by capping values
        if equity > 1e15 or equity < -1e15:
            equity = self.capital
        
        self.equity_curve.append(equity)
        self.timestamps.append(timestamp)
    
    def run_rsi_strategy(
        self,
        df: pd.DataFrame,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        stop_loss_pct: Optional[float] = None,
        take_profit_pct: Optional[float] = None,
    ) -> Dict:
        """
        Run RSI mean reversion strategy
        
        Strategy:
        - BUY when RSI < oversold threshold (default 30)
        - SELL when RSI > overbought threshold (default 70)
        - Optional stop loss and take profit
        
        Args:
            df: DataFrame with OHLCV data and indicators
            rsi_period: RSI period
            rsi_oversold: RSI level for buy signal
            rsi_overbought: RSI level for sell signal
            stop_loss_pct: Stop loss percentage (e.g., 5.0 for 5%)
            take_profit_pct: Take profit percentage (e.g., 15.0 for 15%)
            
        Returns:
            Dictionary with backtest results
        """
        self.reset()
        
        rsi_col = f'RSI_{rsi_period}'
        if rsi_col not in df.columns:
            raise ValueError(f"RSI column '{rsi_col}' not found. Calculate indicators first!")
        
        print(f"\n🚀 Running RSI Strategy Backtest...")
        print(f"   RSI Period: {rsi_period}")
        print(f"   Buy when RSI < {rsi_oversold}")
        print(f"   Sell when RSI > {rsi_overbought}")
        if stop_loss_pct:
            print(f"   Stop Loss: {stop_loss_pct}%")
        if take_profit_pct:
            print(f"   Take Profit: {take_profit_pct}%")
        print(f"   Initial Capital: ${self.initial_capital:,.2f}")
        print(f"   Commission: {self.commission * 100}%")
        print(f"   Slippage: {self.slippage * 100}%")
        print()
        
        # Iterate through data
        for i, (timestamp, row) in enumerate(df.iterrows()):
            price = row['close']
            rsi = row[rsi_col]
            
            # Skip if RSI not yet calculated
            if pd.isna(rsi):
                continue
            
            # Check stop loss / take profit
            if self.position and self.position.is_open:
                current_pnl_pct = ((price - self.position.entry_price) / self.position.entry_price) * 100
                
                if stop_loss_pct and current_pnl_pct <= -stop_loss_pct:
                    self.sell(timestamp, price)
                    continue
                
                if take_profit_pct and current_pnl_pct >= take_profit_pct:
                    self.sell(timestamp, price)
                    continue
            
            # Trading logic
            if not self.position or not self.position.is_open:
                # Look for BUY signal
                if rsi < rsi_oversold:
                    self.buy(timestamp, price)
            else:
                # Look for SELL signal
                if rsi > rsi_overbought:
                    self.sell(timestamp, price)
            
            # Update equity curve
            self.update_equity(timestamp, price)
        
        # Close any open position at the end
        if self.position and self.position.is_open:
            last_timestamp = df.index[-1]
            last_price = df.iloc[-1]['close']
            self.sell(last_timestamp, last_price)
        
        # Calculate performance metrics
        results = self.calculate_metrics(df)
        
        return results
    
    def calculate_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate performance metrics"""
        
        if not self.trades:
            print("⚠️  No trades executed!")
            return {}
        
        # Basic metrics
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl <= 0]
        
        win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0
        
        total_pnl = sum(t.pnl for t in self.trades)
        total_return_pct = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        
        # Profit factor
        gross_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Drawdown
        equity_series = pd.Series(self.equity_curve)
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        # Sharpe Ratio (annualized, assuming hourly data)
        returns = equity_series.pct_change().dropna()
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(365 * 24)  # Annualized
        else:
            sharpe_ratio = 0
        
        # Trade duration
        durations = [t.duration for t in self.trades if t.duration]
        avg_duration = np.mean([d.total_seconds() / 3600 for d in durations]) if durations else 0  # hours
        
        # Results
        results = {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return_pct': total_return_pct,
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'avg_trade_duration_hours': avg_duration,
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'timestamps': self.timestamps,
        }
        
        return results
    
    def print_results(self, results: Dict):
        """Print backtest results"""
        
        print("\n" + "="*60)
        print("📊 BACKTEST RESULTS")
        print("="*60)
        
        print(f"\n💰 Capital:")
        print(f"   Initial: ${results['initial_capital']:,.2f}")
        print(f"   Final:   ${results['final_capital']:,.2f}")
        print(f"   P&L:     ${results['total_pnl']:,.2f}")
        
        color = "🟢" if results['total_return_pct'] > 0 else "🔴"
        print(f"   Return:  {color} {results['total_return_pct']:.2f}%")
        
        print(f"\n📈 Trading:")
        print(f"   Total Trades:   {results['total_trades']}")
        print(f"   Winning Trades: {results['winning_trades']} ({results['win_rate']:.1f}%)")
        print(f"   Losing Trades:  {results['losing_trades']}")
        print(f"   Avg Win:        ${results['avg_win']:.2f}")
        print(f"   Avg Loss:       ${results['avg_loss']:.2f}")
        print(f"   Profit Factor:  {results['profit_factor']:.2f}")
        
        print(f"\n📉 Risk:")
        print(f"   Max Drawdown:   {results['max_drawdown']:.2f}%")
        print(f"   Sharpe Ratio:   {results['sharpe_ratio']:.2f}")
        
        print(f"\n⏱️  Duration:")
        print(f"   Avg Trade:      {results['avg_trade_duration_hours']:.1f} hours")
        
        print("\n" + "="*60)


# Quick test
if __name__ == "__main__":
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='H')
    
    # Simulate price data with trend and noise
    prices = 100 + np.cumsum(np.random.randn(1000) * 2)
    
    df = pd.DataFrame({
        'close': prices,
        'high': prices + np.random.rand(1000) * 2,
        'low': prices - np.random.rand(1000) * 2,
        'open': prices + np.random.randn(1000),
        'volume': np.random.randint(1000, 10000, 1000)
    }, index=dates)
    
    # Calculate RSI
    from indicators import TechnicalIndicators
    df['RSI_14'] = TechnicalIndicators.calculate_rsi(df['close'], 14)
    
    # Run backtest
    engine = BacktestEngine(initial_capital=10000, commission=0.1)
    results = engine.run_rsi_strategy(df, rsi_oversold=30, rsi_overbought=70)
    
    engine.print_results(results)

