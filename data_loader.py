import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time
import os
import streamlit as st

class BTCLoader:
    def __init__(self, use_mock_data=False):
        self.use_mock_data = use_mock_data
        self.client = self._init_client()
    
    def _init_client(self, retries=3):
        """Initialize Binance client with retry logic"""
        if self.use_mock_data:
            return None
            
        for attempt in range(retries):
            try:
                return Client(
                    api_key=os.getenv('BINANCE_API_KEY'),  # From Streamlit secrets
                    api_secret=os.getenv('BINANCE_API_SECRET')
                )
            except BinanceAPIException as e:
                if attempt == retries - 1:
                    st.error(f"Binance API failed after {retries} attempts: {str(e)}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff

    def get_historical_data(self, timeframe='1h', limit=100):
        """Fetch data with fallback to mock data"""
        if self.use_mock_data or not self.client:
            return self._get_mock_data(limit)
            
        try:
            klines = self.client.get_klines(
                symbol="BTCUSDT",
                interval=timeframe,
                limit=limit
            )
            return self._process_data(klines)
        except Exception as e:
            st.warning(f"Using mock data (API failed: {str(e)})")
            return self._get_mock_data(limit)

    def _process_data(self, klines):
        """Convert Binance API response to DataFrame"""
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        
        # Convert columns
        numeric_cols = ["open", "high", "low", "close", "volume"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        
        return df[["timestamp", "open", "high", "low", "close", "volume"]]

    def _get_mock_data(self, limit):
        """Generate realistic mock data"""
        dates = pd.date_range(end=pd.Timestamp.now(), periods=limit, freq='H')
        prices = [40000 + i*100 + (i%10)*500 for i in range(limit)]  # Volatility pattern
        return pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p + 200 for p in prices],
            'low': [p - 200 for p in prices],
            'close': [p + 50 for p in prices],
            'volume': [1000 + i*50 for i in range(limit)]
        })

# Example usage:
if __name__ == "__main__":
    loader = BTCLoader(use_mock_data=True)  # Set False for real data
    data = loader.get_historical_data()
    print(data.head())
