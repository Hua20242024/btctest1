import pandas as pd
import requests
import streamlit as st
from datetime import datetime, timedelta

class BTCLoader:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def get_historical_data(self, timeframe='1h', limit=100):
        """Fetch BTC/USD data with parameters matching app.py"""
        try:
            # Convert limit to days (CoinGecko requires days)
            days = max(1, limit // 24)  # At least 1 day
            
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'hourly' if timeframe[-1] == 'h' else 'daily'
            }
            
            response = requests.get(
                f"{self.base_url}/coins/bitcoin/market_chart",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            prices = data['prices'][:limit]  # Trim to requested limit
            
            df = pd.DataFrame(prices, columns=['timestamp', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Generate OHLCV data from close prices
            df['open'] = df['close'].shift(1).fillna(df['close'])
            df['high'] = df[['open', 'close']].max(axis=1)
            df['low'] = df[['open', 'close']].min(axis=1)
            df['volume'] = 1000  # Placeholder value
            
            return df[['open', 'high', 'low', 'close', 'volume']].dropna()
            
        except Exception as e:
            st.error(f"API Error: {str(e)} - Using mock data")
            return self._get_mock_data(timeframe, limit)

    def _get_mock_data(self, timeframe, limit):
        """Generate realistic mock data with timeframe support"""
        freq_map = {
            '1h': 'H',
            '4h': '4H',
            '1d': 'D'
        }
        
        dates = pd.date_range(
            end=pd.Timestamp.now(), 
            periods=limit, 
            freq=freq_map.get(timeframe, 'H')
        )
        
        base_prices = [40000 + i*10 for i in range(limit)]
        volatility = [300 * (i % 24 - 12)/12 for i in range(limit)]
        
        return pd.DataFrame({
            'timestamp': dates,
            'open': base_prices,
            'high': [p + abs(v) + 200 for p,v in zip(base_prices, volatility)],
            'low': [p - abs(v) - 200 for p,v in zip(base_prices, volatility)],
            'close': [p + v for p,v in zip(base_prices, volatility)],
            'volume': [1000 + i%24*500 for i in range(limit)]
        }).set_index('timestamp')
