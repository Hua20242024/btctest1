import pandas as pd
from binance.client import Client

class BTCLoader:
    def __init__(self):
        self.client = Client()  # Public data doesn't need API keys
    
    def get_historical_data(self, timeframe='1h', limit=100):
        """Fetch BTC/USDT data from Binance"""
        klines = self.client.get_klines(
            symbol="BTCUSDT",
            interval=timeframe,
            limit=limit
        )
        
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        
        # Convert columns
        numeric_cols = ["open", "high", "low", "close", "volume"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        
        return df[["timestamp", "open", "high", "low", "close"]]
