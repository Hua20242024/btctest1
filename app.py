import streamlit as st
import pandas as pd
from data_loader import BTCLoader
from strategy import BTCStrategy
from visualizations import BTCVisualizations

# App Configuration
st.set_page_config(
    page_title="BTC Trading Signals",
    page_icon="🚀",
    layout="wide"
)

# Sidebar Controls
st.sidebar.header("Settings")
timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["1h", "4h", "1d"],
    index=0,
    help="Select candle timeframe"
)

days_to_load = st.sidebar.slider(
    "Days of data to load",
    min_value=1,
    max_value=90,
    value=7,
    help="Number of days of historical data to fetch"
)

# Title and Description
st.title("🚀 BTC/USDT Trading Signals")
st.markdown("""
    **Strategy Rules:**
    - Buy when Price > EMA 144 + MACD Bullish Crossover + RSI > 50
    - Sell when Price < EMA 144 + MACD Bearish Crossover + RSI < 50
""")

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(timeframe, days):
    loader = BTCLoader()
    return loader.get_historical_data(timeframe=timeframe, limit=days*24)

# Data Loading
try:
    with st.spinner("Loading BTC data..."):
        df = load_data(timeframe, days_to_load)
        
        if df.empty:
            st.error("No data loaded - using mock data")
            df = BTCLoader()._get_mock_data(timeframe, days_to_load*24)
            
        strategy = BTCStrategy(df)
        df_with_signals = strategy.generate_signals()
        
        # Display Latest Signal
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

        # Visualizations
        st.plotly_chart(
            BTCVisualizations(df_with_signals), 
            use_container_width=True
        )
        
        # Recent Signals Table
        st.subheader("Recent Trading Signals")
        signals_df = df_with_signals[df_with_signals["signal"] != 0].tail(5)
        st.dataframe(
            signals_df[["close", "ema_144", "rsi", "signal"]].sort_index(ascending=False),
            column_config={
                "close": st.column_config.NumberColumn("Price", format="$%.2f"),
                "ema_144": st.column_config.NumberColumn("EMA 144", format="$%.2f"),
                "rsi": st.column_config.NumberColumn("RSI", format="%.2f"),
                "signal": st.column_config.NumberColumn("Signal", format="%d")
            }
        )

except Exception as e:
    st.error(f"Application error: {str(e)}")
    st.warning("Loading mock data instead...")
    df = BTCLoader()._get_mock_data(timeframe, days_to_load*24)
    st.dataframe(df.tail())
