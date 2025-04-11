import streamlit as st
from data_loader import BTCLoader
from strategy import BTCStrategy
from visualizations import BTCVisualizations

# App Config
st.set_page_config(page_title="BTC Trading Signals", layout="wide")
st.title("🚀 BTC Trading Dashboard")

# Data Loading
loader = BTCLoader()
df = loader.get_historical_data(timeframe='1h', limit=100)

# Strategy
strategy = BTCStrategy(df)
signals = strategy.generate_signals()

# Visualizations
fig = BTCVisualizations(signals)
st.plotly_chart(fig, use_container_width=True)

# Latest Signal
latest = signals.iloc[-1]
if latest['signal'] == 1:
    st.success("✅ BUY SIGNAL (Price > EMA 144, MACD ↑, RSI > 50)")
elif latest['signal'] == -1:
    st.error("❌ SELL SIGNAL (Price < EMA 144, MACD ↓, RSI < 50)")
else:
    st.info("🟡 HOLD (No Strong Signal)")

# Raw Data
st.dataframe(signals.tail())
