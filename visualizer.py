"""
Visualization - Chart results
Plots equity curve, trades, indicators
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, List
import numpy as np


class Visualizer:
    """Visualize backtest results"""
    
    @staticmethod
    def plot_equity_curve(results: Dict, title: str = "Equity Curve"):
        """Plot equity curve over time"""
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        timestamps = results['timestamps']
        equity = results['equity_curve']
        
        # Ensure arrays have same length
        min_len = min(len(timestamps), len(equity))
        timestamps = timestamps[:min_len]
        equity = equity[:min_len]
        
        ax.plot(timestamps, equity, linewidth=2, color='#2E86AB', label='Equity')
        ax.axhline(
            y=results['initial_capital'],
            color='gray',
            linestyle='--',
            alpha=0.5,
            label='Initial Capital'
        )
        
        # Fill area
        ax.fill_between(
            timestamps,
            results['initial_capital'],
            equity,
            where=(np.array(equity) >= results['initial_capital']),
            color='green',
            alpha=0.1
        )
        ax.fill_between(
            timestamps,
            results['initial_capital'],
            equity,
            where=(np.array(equity) < results['initial_capital']),
            color='red',
            alpha=0.1
        )
        
        # Labels
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Equity ($)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_trades(df: pd.DataFrame, results: Dict, show_rsi: bool = True):
        """Plot price with trade entry/exit points"""
        
        trades = results['trades']
        
        if show_rsi:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                            gridspec_kw={'height_ratios': [3, 1]})
        else:
            fig, ax1 = plt.subplots(figsize=(14, 6))
        
        # Plot price
        ax1.plot(df.index, df['close'], linewidth=1.5, color='black', label='Price', alpha=0.7)
        
        # Plot trades
        for trade in trades:
            # Entry point
            ax1.scatter(
                trade.entry_time,
                trade.entry_price,
                color='green',
                marker='^',
                s=100,
                zorder=5,
                label='Buy' if trade == trades[0] else ""
            )
            
            # Exit point
            if trade.exit_time:
                exit_color = 'darkgreen' if trade.pnl > 0 else 'darkred'
                ax1.scatter(
                    trade.exit_time,
                    trade.exit_price,
                    color=exit_color,
                    marker='v',
                    s=100,
                    zorder=5,
                    label='Sell (Profit)' if trade.pnl > 0 and trade == trades[0] else 
                          'Sell (Loss)' if trade.pnl < 0 and trade == trades[0] else ""
                )
                
                # Draw line connecting entry to exit
                ax1.plot(
                    [trade.entry_time, trade.exit_time],
                    [trade.entry_price, trade.exit_price],
                    color=exit_color,
                    linestyle='--',
                    alpha=0.3,
                    linewidth=1
                )
        
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.set_title('Price Chart with Trade Signals', fontsize=14, fontweight='bold')
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # Plot RSI
        if show_rsi:
            # Find RSI column
            rsi_col = [col for col in df.columns if col.startswith('RSI_')]
            if rsi_col:
                ax2.plot(df.index, df[rsi_col[0]], linewidth=1.5, color='purple', label='RSI')
                
                # RSI levels
                ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Overbought (70)')
                ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Oversold (30)')
                ax2.axhline(y=50, color='gray', linestyle=':', alpha=0.3)
                
                ax2.fill_between(df.index, 70, 100, alpha=0.1, color='red')
                ax2.fill_between(df.index, 0, 30, alpha=0.1, color='green')
                
                ax2.set_ylabel('RSI', fontsize=12)
                ax2.set_xlabel('Date', fontsize=12)
                ax2.set_ylim(0, 100)
                ax2.legend(loc='best')
                ax2.grid(True, alpha=0.3)
        
        # Format x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        if show_rsi:
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        else:
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_drawdown(results: Dict):
        """Plot drawdown over time"""
        
        fig, ax = plt.subplots(figsize=(14, 5))
        
        equity_series = pd.Series(results['equity_curve'], index=results['timestamps'])
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max * 100
        
        ax.fill_between(drawdown.index, 0, drawdown, color='red', alpha=0.3)
        ax.plot(drawdown.index, drawdown, color='darkred', linewidth=1.5)
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.set_title('Drawdown Over Time', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_trade_distribution(results: Dict):
        """Plot trade P&L distribution"""
        
        trades = results['trades']
        pnls = [t.pnl_percent for t in trades]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram
        ax1.hist(pnls, bins=30, color='steelblue', edgecolor='black', alpha=0.7)
        ax1.axvline(x=0, color='red', linestyle='--', linewidth=2)
        ax1.set_xlabel('P&L (%)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_title('Trade P&L Distribution', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Win/Loss pie chart
        winning = len([p for p in pnls if p > 0])
        losing = len([p for p in pnls if p <= 0])
        
        colors = ['#28a745', '#dc3545']
        ax2.pie(
            [winning, losing],
            labels=[f'Wins: {winning}', f'Losses: {losing}'],
            colors=colors,
            autopct='%1.1f%%',
            startangle=90
        )
        ax2.set_title('Win/Loss Ratio', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_monthly_returns(results: Dict):
        """Plot monthly returns heatmap"""
        
        equity_series = pd.Series(results['equity_curve'], index=results['timestamps'])
        monthly_returns = equity_series.resample('M').last().pct_change() * 100
        
        # Create year x month matrix
        returns_df = pd.DataFrame({
            'Year': monthly_returns.index.year,
            'Month': monthly_returns.index.month,
            'Return': monthly_returns.values
        })
        
        pivot = returns_df.pivot(index='Year', columns='Month', values='Return')
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Heatmap
        im = ax.imshow(pivot.values, cmap='RdYlGn', aspect='auto', vmin=-10, vmax=10)
        
        # Labels
        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        ax.set_yticklabels(pivot.index)
        
        # Annotate cells
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                value = pivot.values[i, j]
                if not np.isnan(value):
                    text = ax.text(j, i, f'{value:.1f}%',
                                 ha="center", va="center", color="black", fontsize=9)
        
        ax.set_title('Monthly Returns Heatmap', fontsize=14, fontweight='bold')
        fig.colorbar(im, ax=ax, label='Return (%)')
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_dashboard(df: pd.DataFrame, results: Dict, save_path: str = None):
        """Create comprehensive dashboard"""
        
        # Create all plots
        print("📊 Creating visualizations...")
        
        fig1 = Visualizer.plot_equity_curve(results)
        fig2 = Visualizer.plot_trades(df, results)
        fig3 = Visualizer.plot_drawdown(results)
        fig4 = Visualizer.plot_trade_distribution(results)
        
        if save_path:
            fig1.savefig(f'{save_path}_equity.png', dpi=300, bbox_inches='tight')
            fig2.savefig(f'{save_path}_trades.png', dpi=300, bbox_inches='tight')
            fig3.savefig(f'{save_path}_drawdown.png', dpi=300, bbox_inches='tight')
            fig4.savefig(f'{save_path}_distribution.png', dpi=300, bbox_inches='tight')
            print(f"💾 Charts saved to {save_path}_*.png")
        
        plt.show()
        
        return fig1, fig2, fig3, fig4


# Quick test
if __name__ == "__main__":
    print("Visualizer module loaded. Use with backtest results.")

