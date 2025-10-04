"""
Technical Indicators
Implements RSI, MACD, MA, Bollinger Bands, etc.
"""

import pandas as pd
import numpy as np
from typing import Tuple


class TechnicalIndicators:
    """Calculate technical indicators for trading strategies"""
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            prices: Series of closing prices
            period: RSI period (default 14)
            
        Returns:
            Series with RSI values (0-100)
        """
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period, min_periods=period).mean()
        avg_losses = losses.rolling(window=period, min_periods=period).mean()
        
        # Calculate RS (Relative Strength)
        rs = avg_gains / avg_losses
        
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_sma(prices: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA)
        
        Args:
            prices: Series of closing prices
            period: Moving average period
            
        Returns:
            Series with SMA values
        """
        return prices.rolling(window=period, min_periods=period).mean()
    
    @staticmethod
    def calculate_ema(prices: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA)
        
        Args:
            prices: Series of closing prices
            period: EMA period
            
        Returns:
            Series with EMA values
        """
        return prices.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_macd(
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: Series of closing prices
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line period (default 9)
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        # Calculate EMAs
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        
        # Histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(
        prices: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            prices: Series of closing prices
            period: Moving average period
            std_dev: Number of standard deviations
            
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        # Middle band (SMA)
        middle = prices.rolling(window=period, min_periods=period).mean()
        
        # Standard deviation
        std = prices.rolling(window=period, min_periods=period).std()
        
        # Upper and lower bands
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper, middle, lower
    
    @staticmethod
    def calculate_atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate Average True Range (ATR)
        
        Args:
            high: Series of high prices
            low: Series of low prices
            close: Series of close prices
            period: ATR period
            
        Returns:
            Series with ATR values
        """
        # True Range components
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        # True Range (max of the three)
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR (moving average of TR)
        atr = tr.rolling(window=period, min_periods=period).mean()
        
        return atr
    
    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all technical indicators to DataFrame
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with indicators added
        """
        # RSI
        df['RSI_14'] = TechnicalIndicators.calculate_rsi(df['close'], 14)
        df['RSI_20'] = TechnicalIndicators.calculate_rsi(df['close'], 20)
        
        # Moving Averages
        df['SMA_20'] = TechnicalIndicators.calculate_sma(df['close'], 20)
        df['SMA_50'] = TechnicalIndicators.calculate_sma(df['close'], 50)
        df['SMA_200'] = TechnicalIndicators.calculate_sma(df['close'], 200)
        
        df['EMA_7'] = TechnicalIndicators.calculate_ema(df['close'], 7)
        df['EMA_25'] = TechnicalIndicators.calculate_ema(df['close'], 25)
        df['EMA_99'] = TechnicalIndicators.calculate_ema(df['close'], 99)
        
        # MACD
        macd, signal, histogram = TechnicalIndicators.calculate_macd(df['close'])
        df['MACD'] = macd
        df['MACD_signal'] = signal
        df['MACD_histogram'] = histogram
        
        # Bollinger Bands
        upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(df['close'])
        df['BB_upper'] = upper
        df['BB_middle'] = middle
        df['BB_lower'] = lower
        
        # ATR
        df['ATR_14'] = TechnicalIndicators.calculate_atr(
            df['high'], df['low'], df['close'], 14
        )
        
        print("✅ All indicators calculated!")
        return df


# Quick test
if __name__ == "__main__":
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    prices = pd.Series(
        100 + np.cumsum(np.random.randn(100) * 2),
        index=dates
    )
    
    # Calculate RSI
    rsi = TechnicalIndicators.calculate_rsi(prices)
    
    print("📊 RSI Sample:")
    print(rsi.tail(10))
    
    # Calculate MACD
    macd, signal, hist = TechnicalIndicators.calculate_macd(prices)
    
    print("\n📈 MACD Sample:")
    print(f"MACD: {macd.iloc[-1]:.2f}")
    print(f"Signal: {signal.iloc[-1]:.2f}")
    print(f"Histogram: {hist.iloc[-1]:.2f}")

