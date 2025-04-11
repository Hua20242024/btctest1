from ta.trend import MACD, EMAIndicator
from ta.momentum import RSIIndicator

class BTCStrategy:
    def __init__(self, df):
        self.df = df.copy()
        self._calculate_indicators()
    
    def _calculate_indicators(self):
        # EMA 144
        self.df['ema_144'] = EMAIndicator(self.df["close"], window=144).ema_indicator()
        
        # MACD
        macd = MACD(self.df["close"], window_slow=26, window_fast=12, window_sign=9)
        self.df['macd'] = macd.macd()
        self.df['macd_signal'] = macd.macd_signal()
        
        # RSI
        self.df['rsi'] = RSIIndicator(self.df["close"], window=14).rsi()
    
    def generate_signals(self):
        """Returns DataFrame with signals (1=buy, -1=sell)"""
        self.df['signal'] = 0
        # Buy when price > EMA144, MACD crossover, and RSI > 50
        self.df.loc[
            (self.df["close"] > self.df["ema_144"]) & 
            (self.df["macd"] > self.df["macd_signal"]) & 
            (self.df["rsi"] > 50), 'signal'
        ] = 1
        # Sell when opposite conditions
        self.df.loc[
            (self.df["close"] < self.df["ema_144"]) & 
            (self.df["macd"] < self.df["macd_signal"]) & 
            (self.df["rsi"] < 50), 'signal'
        ] = -1
        return self.df
