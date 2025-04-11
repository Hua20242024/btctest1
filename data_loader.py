import pandas as pd
import requests
import streamlit as st
from datetime import datetime, timedelta
import numpy as np

class BTCLoader:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.last_fetch = None
        self.cached_data = None

    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_historical_data(_self, timeframe='1h', days=7):
        """Smarter data fetching with rate limit handling"""
        try:
            # CoinGecko free tier limits (50 calls/minute)
            if _self.last_fetch and (datetime.now() - _self.last_fetch).seconds < 12:
                raise Exception("Rate limit cooldown")

            params = {
                'vs_currency': 'usd',
                'days': min(days, 90),  # Max 90 days for free tier
                'interval': 'hourly' if timeframe.endswith('h') else 'daily'
            }

            response = requests.get(
                f"{_self.base_url}/coins/bitcoin/market_chart",
                params=params,
                timeout=15
            )
            response.raise_for_status()

            data = response.json()
            _self.last_fetch = datetime.now()
            
            # Process to OHLCV
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Generate realistic OHLCV from close prices
            df = _self._enhance_dataframe(df, timeframe)
            return df

        except Exception as e:
            st.warning(f"Using mock data: {str(e)}")
            return _self._get_mock_data(timeframe, days)

    def _enhance_dataframe(self, df, timeframe):
        """Convert basic price data to OHLCV format"""
        df.set_index('timestamp', inplace=True)
        
        # Resample to exact timeframe
        freq = '1H' if timeframe == '1h' else '4H' if timeframe == '4h' else '1D'
        df = df.resample(freq).agg({
            'close': 'last'
        }).ffill()
        
        # Generate synthetic but realistic OHLCV
        df['open'] = df['close'].shift(1).fillna(df['close'])
        volatility = 0.002 * (np.sin(np.arange(len(df)) * 0.5) + 1)  # Cyclic volatility
        df['high'] = df['close'] * (1 + volatility)
        df['low'] = df['close'] * (1 - volatility)
        df['volume'] = 1000 + (df.index.astype(int) % 24) * 500  # Daily pattern
        
        return df[['open', 'high', 'low', 'close', 'volume']].dropna()

    def _get_mock_data(self, timeframe, days):
        """Generate ultra-realistic mock data"""
        periods = days * (24 if timeframe == '1h' else 6 if timeframe == '4h' else 1)
        base_date = datetime.now() - timedelta(days=days)
        
        # Realistic price movement simulation
        x = np.linspace(0, 10, periods)
        base_prices = 50000 + 20000 * np.sin(x)  # Major trend
        noise = 3000 * np.random.normal(size=periods)  # Random noise
        daily_pattern = 2000 * np.sin(np.arange(periods) * 0.5)  # Daily cycles
        
        prices = base_prices + noise + daily_pattern
        
        df = pd.DataFrame({
            'timestamp': pd.date_range(start=base_date, periods=periods, freq='H'),
            'open': prices,
            'high': prices + 150 + np.abs(noise),
            'low': prices - 150 - np.abs(noise),
            'close': prices + noise/2,
            'volume': 1000 + (np.arange(periods) % 24) * 500
        }).set_index('timestamp')
        
        # Resample if needed
        if timeframe == '4h':
            df = df.resample('4H').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            })
        elif timeframe == '1d':
            df = df.resample('1D').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            })
            
        return df
