"""
Strong Mic Trading Dashboard
A minimalist trading interface with core mathematical analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pandas_ta as ta

# Page Configuration
st.set_page_config(
    page_title="Trading Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State Initialization
if 'aggression_level' not in st.session_state:
    st.session_state.aggression_level = 5
if 'trade_log' not in st.session_state:
    st.session_state.trade_log = []
if 'market_sync' not in st.session_state:
    st.session_state.market_sync = True

# Styling
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
.stMetric {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid #d3d3d3;
    border-radius: 10px;
    padding: 15px;
}
h1, h2, h3 {
    color: #2d3748 !important;
}
.trade-log {
    font-family: 'Courier New', monospace;
    font-size: 14px;
    padding: 5px;
}
.win {
    color: #22c55e;
    font-weight: bold;
}
.loss {
    color: #ef4444;
    font-weight: bold;
}
.neutral {
    color: #6b7280;
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Trading Dashboard")

# Sidebar - Controls
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Trade Aggression Slider (0-10)
    st.session_state.aggression_level = st.slider(
        "Trade Aggression Level",
        min_value=0,
        max_value=10,
        value=st.session_state.aggression_level,
        help="0 = Conservative, 10 = Aggressive"
    )
    
    aggression_desc = ["Very Conservative", "Conservative", "Moderate-Conservative", "Moderate", 
                      "Moderate", "Moderate", "Moderate-Aggressive", "Aggressive", 
                      "Very Aggressive", "Maximum", "Maximum+"]
    st.info(f"Level {st.session_state.aggression_level}: {aggression_desc[st.session_state.aggression_level]}")
    
    st.markdown("---")
    
    # Market Sync Switch
    st.session_state.market_sync = st.checkbox(
        "Market Data Sync",
        value=st.session_state.market_sync,
        help="Enable/disable market data synchronization"
    )
    
    if st.session_state.market_sync:
        st.success("✅ Market Sync Active")
    else:
        st.warning("⏸️ Market Sync Paused")


# Core Strategy Functions
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators"""
    df.ta.rsi(length=14, append=True)
    df.ta.sma(length=20, append=True)
    df.ta.sma(length=50, append=True)
    return df


def check_signal(df: pd.DataFrame) -> str:
    """Check for trading signals"""
    if len(df) < 50:
        return "NEUTRAL"
        
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    # Golden Cross (SMA 20 crosses above SMA 50)
    if prev_row['SMA_20'] <= prev_row['SMA_50'] and last_row['SMA_20'] > last_row['SMA_50']:
        return "BUY"
        
    # Death Cross (SMA 20 crosses below SMA 50)
    if prev_row['SMA_20'] >= prev_row['SMA_50'] and last_row['SMA_20'] < last_row['SMA_50']:
        return "SELL"
        
    return "NEUTRAL"


def generate_mock_data(symbol: str, periods: int = 100) -> pd.DataFrame:
    """Generate mock OHLCV data for testing"""
    base_price = 50000 if "BTC" in symbol else 3000
    timestamps = pd.date_range(end=datetime.now(), periods=periods, freq='1H')
    
    data = []
    price = base_price
    for ts in timestamps:
        change = np.random.randn() * (base_price * 0.01)
        price += change
        open_price = price
        high = price + abs(np.random.randn() * (base_price * 0.005))
        low = price - abs(np.random.randn() * (base_price * 0.005))
        close_price = price + np.random.randn() * (base_price * 0.005)
        volume = abs(np.random.randn() * 1000)
        
        data.append({
            'timestamp': ts,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'volume': volume
        })
        price = close_price
    
    return pd.DataFrame(data)


# Main Content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Aggression Level", f"{st.session_state.aggression_level}/10")
with col2:
    st.metric("Market Status", "Active" if st.session_state.market_sync else "Paused")
with col3:
    win_count = sum(1 for log in st.session_state.trade_log if log.get('result') == 'WIN')
    total = len(st.session_state.trade_log)
    win_rate = (win_count / total * 100) if total > 0 else 0
    st.metric("Win Rate", f"{win_rate:.1f}%")

st.markdown("---")

# Trading Interface
tab1, tab2 = st.tabs(["📈 Market Analysis", "📜 Trade Log"])

with tab1:
    st.subheader("Market Analysis")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        symbol = st.text_input("Symbol", "BTC/USDT", key="analysis_symbol")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Analyze", use_container_width=True)
    
    if analyze_btn:
        with st.spinner("Analyzing market data..."):
            # Generate mock data
            df = generate_mock_data(symbol)
            df = calculate_indicators(df)
            signal = check_signal(df)
            
            # Display signal
            signal_color = "#22c55e" if signal == "BUY" else "#ef4444" if signal == "SELL" else "#6b7280"
            st.markdown(f"<h2 style='color: {signal_color};'>Signal: {signal}</h2>", unsafe_allow_html=True)
            
            # Display indicators
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("RSI (14)", f"{df['RSI_14'].iloc[-1]:.2f}" if 'RSI_14' in df.columns else "N/A")
            with col2:
                st.metric("SMA (20)", f"{df['SMA_20'].iloc[-1]:.2f}" if 'SMA_20' in df.columns else "N/A")
            with col3:
                st.metric("SMA (50)", f"{df['SMA_50'].iloc[-1]:.2f}" if 'SMA_50' in df.columns else "N/A")
            
            # Display recent data
            st.dataframe(df.tail(10), use_container_width=True)
            
            # Simulated trade execution
            if signal in ["BUY", "SELL"]:
                trade_result = "WIN" if np.random.random() > 0.4 else "LOSS"
                st.session_state.trade_log.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "symbol": symbol,
                    "signal": signal,
                    "result": trade_result,
                    "aggression": st.session_state.aggression_level
                })
                
                if trade_result == "WIN":
                    st.success(f"✅ Trade executed: {signal} {symbol}")
                else:
                    st.error(f"❌ Trade closed: {signal} {symbol}")

with tab2:
    st.subheader("5-Line Rolling Trade Feed")
    
    if len(st.session_state.trade_log) == 0:
        st.info("No trades logged yet. Execute trades in the Market Analysis tab.")
    else:
        # Display last 5 trades
        recent_trades = st.session_state.trade_log[-5:]
        for trade in reversed(recent_trades):
            result_class = "win" if trade["result"] == "WIN" else "loss"
            st.markdown(
                f"<div class='trade-log'>"
                f"<span class='{result_class}'>[{trade['result']}]</span> "
                f"{trade['time']} | {trade['symbol']} | {trade['signal']} | "
                f"Aggression: {trade['aggression']}/10"
                f"</div>",
                unsafe_allow_html=True
            )
        
        # Statistics
        st.markdown("---")
        wins = sum(1 for t in st.session_state.trade_log if t['result'] == 'WIN')
        losses = sum(1 for t in st.session_state.trade_log if t['result'] == 'LOSS')
        total = len(st.session_state.trade_log)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Trades", total)
        with col2:
            st.metric("Wins", wins, delta=f"{wins/total*100:.1f}%" if total > 0 else "0%")
        with col3:
            st.metric("Losses", losses, delta=f"-{losses/total*100:.1f}%" if total > 0 else "0%", delta_color="inverse")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #6b7280; font-size: 12px;'>"
    "Trading Dashboard | Mathematical Analysis Engine"
    "</p>",
    unsafe_allow_html=True
)
