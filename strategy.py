import pandas as pd
from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator

class BTCStrategy:
    def __init__(self, df):
        self.df = df.copy()
        self.calculate_indicators()
        self.generate_signals()
    
    def calculate_indicators(self):
        """Calculate technical indicators"""
        # MACD
        macd = MACD(self.df["close"], window_slow=26, window_fast=12, window_sign=9)
        self.df["macd"] = macd.macd()
        self.df["macd_signal"] = macd.macd_signal()
        self.df["macd_hist"] = macd.macd_diff()
        
        # EMA 144
        ema = EMAIndicator(self.df["close"], window=144)
        self.df["ema_144"] = ema.ema_indicator()
        
        # RSI
        rsi = RSIIndicator(self.df["close"], window=14)
        self.df["rsi"] = rsi.rsi()
        
        return self.df
    
    def generate_signals(self):
        """Generate buy/sell signals based on strategy"""
        self.df["signal"] = 0  # Initialize with no signal
        
        # Buy signal: Price > EMA 144 + MACD crossover + RSI > 50
        self.df.loc[
            (self.df["close"] > self.df["ema_144"]) & 
            (self.df["macd"] > self.df["macd_signal"]) & 
            (self.df["rsi"] > 50), "signal"
        ] = 1
        
        # Sell signal: Price < EMA 144 + MACD crossunder + RSI < 50
        self.df.loc[
            (self.df["close"] < self.df["ema_144"]) & 
            (self.df["macd"] < self.df["macd_signal"]) & 
            (self.df["rsi"] < 50), "signal"
        ] = -1
        
        # Mark signal points
        self.df["entry"] = self.df["signal"].diff()
        return self.df