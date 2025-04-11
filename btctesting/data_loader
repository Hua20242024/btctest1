import pandas as pd
from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()

class BTCLoader:
    def __init__(self):
        self.client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))
    
    def get_historical_data(self, timeframe='1d', limit=500):
        """Fetch historical BTC/USDT data from Binance"""
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
        
        # Convert columns to numeric
        numeric_cols = ["open", "high", "low", "close", "volume"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
        
        # Convert timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        
        return df
