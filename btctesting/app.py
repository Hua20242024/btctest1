import streamlit as st
import pandas as pd
# Change these imports:
from btctesting.data_loader import BTCLoader  # Must match the underscore
from btctesting.strategy import BTCStrategy
from btctesting.visuals import BTCVisualizations
# Page configuration
st.set_page_config(
    page_title="BTC Trading Signals",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🚀 BTC/USDT Trading Signals")
st.markdown("""
    This app analyzes BTC/USDT price data and generates buy/sell signals based on:
    - **EMA 144** (Trend filter)
    - **MACD** (Momentum)
    - **RSI** (Overbought/Oversold)
""")

# Sidebar controls
st.sidebar.header("Settings")
timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["1d", "4h", "1h"],
    index=0
)

days_to_load = st.sidebar.slider(
    "Days of data to load",
    min_value=30,
    max_value=365,
    value=90
)

# Load data
@st.cache_data
def load_data(timeframe, days):
    loader = BTCLoader()
    limit = days * (24 if timeframe == "1h" else (6 if timeframe == "4h" else 1))
    return loader.get_historical_data(timeframe=timeframe, limit=limit)

df = load_data(timeframe, days_to_load)

# Apply strategy
strategy = BTCStrategy(df)
df_with_signals = strategy.df

# Display signals summary
latest_signal = df_with_signals["signal"].iloc[-1]
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Current Price", f"${df_with_signals['close'].iloc[-1]:,.2f}")

with col2:
    if latest_signal == 1:
        st.success("**Current Signal: BUY**")
    elif latest_signal == -1:
        st.error("**Current Signal: SELL**")
    else:
        st.info("**Current Signal: HOLD**")

with col3:
    st.metric("EMA 144", f"${df_with_signals['ema_144'].iloc[-1]:,.2f}")

# Show the chart
st.subheader("Trading Signals Chart")
visualizer = BTCVisualizations(df_with_signals)
fig = visualizer.create_main_chart()
st.plotly_chart(fig, use_container_width=True)

# Show recent signals
st.subheader("Recent Trading Signals")
signal_df = df_with_signals[df_with_signals["entry"] != 0].tail(10)
st.dataframe(
    signal_df[["close", "ema_144", "rsi", "signal"]].sort_index(ascending=False),
    column_config={
        "close": st.column_config.NumberColumn("Price", format="$%.2f"),
        "ema_144": st.column_config.NumberColumn("EMA 144", format="$%.2f"),
        "rsi": st.column_config.NumberColumn("RSI", format="%.2f"),
        "signal": st.column_config.NumberColumn("Signal", format="%d")
    }
)

# Raw data (optional)
if st.checkbox("Show raw data"):
    st.subheader("Raw Data")
    st.dataframe(df_with_signals.tail(20))
