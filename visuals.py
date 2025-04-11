import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

class BTCVisualizations:
    def __init__(self, df):
        self.df = df
    
    def create_main_chart(self):
        """Create interactive candlestick chart with indicators"""
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            specs=[[{"secondary_y": True}], [{}], [{}]]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=self.df.index,
                open=self.df["open"],
                high=self.df["high"],
                low=self.df["low"],
                close=self.df["close"],
                name="BTC/USDT"
            ),
            row=1, col=1
        )
        
        # EMA 144
        fig.add_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df["ema_144"],
                line=dict(color="orange", width=2),
                name="EMA 144"
            ),
            row=1, col=1
        )
        
        # Buy signals (green arrows)
        buy_signals = self.df[self.df["entry"] == 1]
        fig.add_trace(
            go.Scatter(
                x=buy_signals.index,
                y=buy_signals["low"] * 0.98,
                mode="markers",
                marker=dict(
                    symbol="triangle-up",
                    color="green",
                    size=12
                ),
                name="Buy Signal"
            ),
            row=1, col=1
        )
        
        # Sell signals (red arrows)
        sell_signals = self.df[self.df["entry"] == -1]
        fig.add_trace(
            go.Scatter(
                x=sell_signals.index,
                y=sell_signals["high"] * 1.02,
                mode="markers",
                marker=dict(
                    symbol="triangle-down",
                    color="red",
                    size=12
                ),
                name="Sell Signal"
            ),
            row=1, col=1
        )
        
        # MACD
        fig.add_trace(
            go.Bar(
                x=self.df.index,
                y=self.df["macd_hist"],
                name="MACD Histogram",
                marker_color=np.where(self.df["macd_hist"] < 0, 'red', 'green')
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df["macd"],
                line=dict(color="blue", width=2),
                name="MACD"
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df["macd_signal"],
                line=dict(color="orange", width=2),
                name="Signal Line"
            ),
            row=2, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(
                x=self.df.index,
                y=self.df["rsi"],
                line=dict(color="purple", width=2),
                name="RSI"
            ),
            row=3, col=1
        )
        
        # RSI levels
        fig.add_hline(
            y=30, line_dash="dot",
            annotation_text="Oversold", 
            annotation_position="bottom right",
            row=3, col=1
        )
        
        fig.add_hline(
            y=70, line_dash="dot",
            annotation_text="Overbought", 
            annotation_position="top right",
            row=3, col=1
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            title="BTC/USDT Trading Signals",
            xaxis_rangeslider_visible=False,
            showlegend=True
        )
        
        return fig