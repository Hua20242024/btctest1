import plotly.graph_objects as go
from plotly.subplots import make_subplots

def BTCVisualizations(df):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
    
    # Price + EMA
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='BTC/USDT'
        ), row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['ema_144'],
            line=dict(color='orange', width=2),
            name='EMA 144'
        ), row=1, col=1
    )
    
    # MACD
    fig.add_trace(
        go.Bar(
            x=df['timestamp'],
            y=df['macd'] - df['macd_signal'],
            name='MACD Histogram'
        ), row=2, col=1
    )
    
    fig.update_layout(height=800, title='BTC Trading Signals')
    return fig
