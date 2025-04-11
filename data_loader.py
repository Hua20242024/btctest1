import pandas as pd
import requests
import time
import streamlit as st
from datetime import datetime, timedelta

class BTCLoader:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        
    def get_historical_data(self, days=30):
        """Fetch BTC/USD data from CoinGecko"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            response = requests.get(
                f"{self.base_url}/coins/bitcoin/market_chart",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            prices = data['prices']
            
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Resample to hourly and forward fill
            df = df.resample('1H').ffill()
            
            # Simulate OHLCV from price data
            df['open'] = df['price'].shift(1)
            df['high'] = df[['open', 'price']].max(axis=1)
            df['low'] = df[['open', 'price']].min(axis=1)
            df['close'] = df['price']
            df['volume'] = 1000  # Placeholder
            
            return df[['open', 'high', 'low', 'close', 'volume']].dropna()
            
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return self._get_mock_data(days)

    def _get_mock_data(self, days):
        """Generate realistic mock data"""
        periods = days * 24  # Hours
        dates = pd.date_range(end=pd.Timestamp.now(), periods=periods, freq='H')
        base_prices = [40000 + i*10 for i in range(periods)]
        volatility = [300 * (i % 24 - 12)/12 for i in range(periods)]  # Daily cycle
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': base_prices,
            'high': [p + abs(v) + 200 for p,v in zip(base_prices, volatility)],
            'low': [p - abs(v) - 200 for p,v in zip(base_prices, volatility)],
            'close': [p + v for p,v in zip(base_prices, volatility)],
            'volume': [1000 + i%24*500 for i in range(periods)]  # Daily pattern
        })
        return df.set_index('timestamp')

# Example usage
if __name__ == "__main__":
    loader = BTCLoader()
    print(loader.get_historical_data(7).tail())  # 7 days data
