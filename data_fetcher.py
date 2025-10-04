"""
Data Fetcher - Historical Price Data
Fetches OHLCV data from Binance API
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


class DataFetcher:
    """Fetch historical cryptocurrency price data"""
    
    def __init__(self, base_url: str = "https://api.binance.com"):
        self.base_url = base_url
        
    def fetch_binance_data(
        self,
        symbol: str = "SOLUSDT",
        interval: str = "1h",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Fetch historical data from Binance
        
        Args:
            symbol: Trading pair (e.g., SOLUSDT, BTCUSDT)
            interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            limit: Max number of candles (max 1000 per request)
            
        Returns:
            DataFrame with OHLCV data
        """
        
        # Convert dates to timestamps
        if start_date:
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
        else:
            # Default: 1 year ago
            start_ts = int((datetime.now() - timedelta(days=365)).timestamp() * 1000)
            
        if end_date:
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
        else:
            end_ts = int(datetime.now().timestamp() * 1000)
        
        # Fetch data in chunks (Binance limit is 1000 candles per request)
        all_data = []
        current_start = start_ts
        
        while current_start < end_ts:
            url = f"{self.base_url}/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'startTime': current_start,
                'endTime': end_ts,
                'limit': limit
            }
            
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                    
                all_data.extend(data)
                
                # Update start time for next request
                current_start = data[-1][0] + 1  # Last timestamp + 1ms
                
                print(f"✅ Fetched {len(data)} candles (Total: {len(all_data)})")
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Error fetching data: {e}")
                break
        
        if not all_data:
            raise ValueError("No data fetched!")
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convert types
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['date'] = df['timestamp'].dt.date
        
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        # Set timestamp as index
        df.set_index('timestamp', inplace=True)
        
        # Keep only essential columns
        df = df[['open', 'high', 'low', 'close', 'volume', 'date']]
        
        print(f"\n📊 Data Summary:")
        print(f"   Symbol: {symbol}")
        print(f"   Interval: {interval}")
        print(f"   Period: {df.index[0]} to {df.index[-1]}")
        print(f"   Total Candles: {len(df)}")
        print(f"   Price Range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        
        return df
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = "historical_data.csv"):
        """Save DataFrame to CSV"""
        df.to_csv(filename)
        print(f"💾 Data saved to {filename}")
    
    def load_from_csv(self, filename: str = "historical_data.csv") -> pd.DataFrame:
        """Load DataFrame from CSV"""
        df = pd.read_csv(filename, index_col='timestamp', parse_dates=True)
        print(f"📂 Data loaded from {filename}")
        return df


# Quick test
if __name__ == "__main__":
    fetcher = DataFetcher()
    
    # Fetch SOL/USDT data for last 6 months (1 hour candles)
    df = fetcher.fetch_binance_data(
        symbol="SOLUSDT",
        interval="1h",
        start_date="2024-04-01",
        end_date="2024-10-04",
    )
    
    print("\n📈 Sample Data:")
    print(df.head())
    print("\n" + "="*60)
    print(df.tail())
    
    # Save to CSV
    fetcher.save_to_csv(df, "SOL_USDT_1h.csv")

