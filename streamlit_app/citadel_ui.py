"""
Citadel UI - V19-G Framework
Modular Streamlit interface for Pioneer Trader
Implements Zen and Overkill visualization modes
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import numpy as np
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
RANDOM_SEED = 42  # For reproducible sample data generation

# Page Configuration
st.set_page_config(
    page_title="Citadel UI - V19-G",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
    <style>
    .stMetric {
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 5px;
    }
    .trade-feed {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        background-color: #0E1117;
        padding: 10px;
        border-radius: 5px;
        height: 150px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'token' not in st.session_state:
    st.session_state.token = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Zen"
if 'trade_aggression' not in st.session_state:
    st.session_state.trade_aggression = 5
if 'live_trades' not in st.session_state:
    st.session_state.live_trades = []

# Bio-Sync Authentication (using backend/routers/auth.py)
def authenticate(username, password):
    """Authenticate user via Bio-Sync (backend OAuth2/JWT)"""
    try:
        res = requests.post(
            f"{API_URL}/auth/login",
            data={"username": username, "password": password}
        )
        if res.status_code == 200:
            return res.json()["access_token"]
    except Exception as e:
        st.error(f"Bio-Sync verification failed: {e}")
    return None

def verify_token(token):
    """Verify current token with backend"""
    try:
        res = requests.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        return res.status_code == 200
    except:
        return False

# Sidebar - Bio-Sync Authentication & Controls
with st.sidebar:
    st.header("🛡️ Bio-Sync Authentication")
    
    if not st.session_state.token:
        st.info("Please authenticate to access Citadel UI")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Authenticate", type="primary"):
            token = authenticate(username, password)
            if token:
                st.session_state.token = token
                st.success("✅ Bio-Sync Verified")
                st.rerun()
            else:
                st.error("❌ Authentication Failed")
    else:
        # Verify token is still valid
        if verify_token(st.session_state.token):
            st.success("✅ Bio-Sync Active")
            if st.button("Logout"):
                st.session_state.token = None
                st.rerun()
        else:
            st.error("❌ Session Expired")
            st.session_state.token = None
            st.rerun()
    
    st.divider()
    
    # System Status
    st.header("📡 System Status")
    try:
        health = requests.get(f"{API_URL}/telemetry/health").json()
        st.metric("Backend", "Online", delta=health.get('mode', 'N/A'))
    except Exception as e:
        st.metric("Backend", "Offline", delta="ERROR")
    
    st.divider()
    
    # View Mode Toggle
    st.header("🎨 Visualization Mode")
    st.session_state.view_mode = st.radio(
        "Select Mode",
        ["Zen", "Overkill"],
        help="Zen: Minimalist line charts | Overkill: Dense candlesticks + volume"
    )
    
    st.divider()
    
    # Trade Aggression Slider
    st.header("⚡ Trade Aggression")
    st.session_state.trade_aggression = st.slider(
        "Aggression Level",
        min_value=0,
        max_value=10,
        value=st.session_state.trade_aggression,
        help="0 = Conservative | 10 = Maximum Aggression"
    )
    
    # Aggression indicator
    if st.session_state.trade_aggression <= 3:
        st.info("🐢 Conservative Mode")
    elif st.session_state.trade_aggression <= 7:
        st.warning("⚡ Balanced Mode")
    else:
        st.error("🔥 Aggressive Mode")

# Main Content - Only if authenticated
if st.session_state.token:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    st.title(f"🏰 Citadel UI - {st.session_state.view_mode} Mode")
    
    # Market Symbol Input
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        symbol = st.text_input("Trading Pair", value="BTC/USDT", key="market_symbol")
    with col2:
        timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
    with col3:
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
    
    # Generate sample data (in production, fetch from backend)
    @st.cache_data(ttl=60)
    def generate_sample_data(symbol, timeframe):
        """Generate sample market data"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='1h')
        # Simulate price movement
        np.random.seed(RANDOM_SEED)
        base_price = 45000 if 'BTC' in symbol else 3000
        prices = base_price + np.cumsum(np.random.randn(100) * 100)
        
        data = pd.DataFrame({
            'timestamp': dates,
            'open': prices + np.random.randn(100) * 50,
            'high': prices + np.random.randn(100) * 100 + 50,
            'low': prices - np.random.randn(100) * 100 - 50,
            'close': prices,
            'volume': np.random.randint(100, 1000, 100)
        })
        return data
    
    market_data = generate_sample_data(symbol, timeframe)
    
    # Visualization based on mode
    if st.session_state.view_mode == "Zen":
        # Zen Mode: Minimalist Line Chart
        st.subheader("📈 Price Movement - Zen View")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=market_data['timestamp'],
            y=market_data['close'],
            mode='lines',
            name='Price',
            line=dict(color='#00D9FF', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 217, 255, 0.1)'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="",
            yaxis_title="Price (USD)",
            showlegend=False,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        # Overkill Mode: Dense Candlesticks + Volume
        st.subheader("📊 Full Market Analysis - Overkill View")
        
        # Candlestick Chart
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=market_data['timestamp'],
            open=market_data['open'],
            high=market_data['high'],
            low=market_data['low'],
            close=market_data['close'],
            name='OHLC',
            increasing_line_color='#00FF00',
            decreasing_line_color='#FF0000'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume Bars
        st.subheader("📊 Volume Analysis")
        
        fig_vol = go.Figure()
        
        colors = ['#00FF00' if market_data['close'].iloc[i] >= market_data['open'].iloc[i] 
                  else '#FF0000' for i in range(len(market_data))]
        
        fig_vol.add_trace(go.Bar(
            x=market_data['timestamp'],
            y=market_data['volume'],
            marker_color=colors,
            name='Volume'
        ))
        
        fig_vol.update_layout(
            template='plotly_dark',
            height=200,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="",
            yaxis_title="Volume",
            showlegend=False,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_vol, use_container_width=True)
    
    # Market Metrics
    st.divider()
    col1, col2, col3, col4, col5 = st.columns(5)
    
    current_price = market_data['close'].iloc[-1]
    price_change = market_data['close'].iloc[-1] - market_data['close'].iloc[-2]
    price_change_pct = (price_change / market_data['close'].iloc[-2]) * 100
    
    with col1:
        st.metric("Current Price", f"${current_price:,.2f}", f"{price_change_pct:+.2f}%")
    with col2:
        st.metric("24h High", f"${market_data['high'].max():,.2f}")
    with col3:
        st.metric("24h Low", f"${market_data['low'].min():,.2f}")
    with col4:
        st.metric("Volume", f"{market_data['volume'].sum():,}")
    with col5:
        st.metric("Aggression", f"{st.session_state.trade_aggression}/10")
    
    # Live Trade Feed (5-line rolling container)
    st.divider()
    st.subheader("📡 Live Trade Feed")
    
    # Simulate live trades
    def add_trade(action, price, amount):
        """Add a trade to the live feed"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        trade = f"[{timestamp}] {action.upper()} {amount:.4f} @ ${price:,.2f}"
        st.session_state.live_trades.insert(0, trade)
        # Keep only last 5 trades
        st.session_state.live_trades = st.session_state.live_trades[:5]
    
    # Trade execution controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        trade_symbol = st.text_input("Symbol", value=symbol, key="trade_symbol")
    with col2:
        trade_side = st.selectbox("Action", ["BUY", "SELL"])
    with col3:
        trade_amount = st.number_input("Amount", min_value=0.001, value=0.01, format="%.4f")
    
    if st.button("⚡ Execute Trade", type="primary"):
        # Simulate trade execution
        add_trade(trade_side, current_price, trade_amount)
        st.success(f"✅ {trade_side} order executed!")
    
    # Display live trade feed
    st.markdown('<div class="trade-feed">', unsafe_allow_html=True)
    if st.session_state.live_trades:
        for trade in st.session_state.live_trades:
            st.code(trade, language=None)
    else:
        st.code("[No recent trades]", language=None)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Strategy Analysis
    st.divider()
    st.subheader("🧠 Strategy Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Analyze Market"):
            with st.spinner("Analyzing market conditions..."):
                try:
                    res = requests.get(
                        f"{API_URL}/strategy/analyze/{symbol}",
                        headers=headers
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.write(f"**Signal:** {data.get('signal', 'N/A')}")
                        if 'data' in data:
                            df = pd.DataFrame(data['data'])
                            st.dataframe(df, use_container_width=True)
                    else:
                        st.error(f"Analysis failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col2:
        if st.button("Load Brain Knowledge"):
            with st.spinner("Loading knowledge base..."):
                try:
                    res = requests.get(f"{API_URL}/brain/knowledge", headers=headers)
                    if res.status_code == 200:
                        st.json(res.json())
                    else:
                        st.error("Failed to load knowledge")
                except Exception as e:
                    st.error(f"Error: {e}")

else:
    # Not authenticated
    st.title("🏰 Citadel UI - V19-G Framework")
    st.warning("🔒 Bio-Sync authentication required. Please login using the sidebar.")
    
    # Display system information
    st.info("""
    **Citadel UI Features:**
    - **Zen Mode**: Minimalist line charts for clean market overview
    - **Overkill Mode**: Dense candlesticks with volume analysis
    - **Trade Aggression**: Adjustable risk level (0-10)
    - **Live Trade Feed**: Real-time 5-line trade display
    - **Bio-Sync Integration**: Secured by backend OAuth2/JWT authentication
    """)
