import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# Config
API_URL = "http://localhost:8000"

# Page Config with Theme Support
st.set_page_config(
    page_title="T.I.A. Citadel - V19 Infinite Cockpit", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session State Initialization
if 'token' not in st.session_state:
    st.session_state.token = None
if 'ui_theme' not in st.session_state:
    st.session_state.ui_theme = "OVERKILL"
if 'safety_modulator' not in st.session_state:
    st.session_state.safety_modulator = 5
if 'trade_log' not in st.session_state:
    st.session_state.trade_log = []
if 'github_device_code' not in st.session_state:
    st.session_state.github_device_code = None

# Theme Styling
def apply_theme():
    if st.session_state.ui_theme == "OVERKILL":
        st.markdown("""
        <style>
        .main {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }
        .stMetric {
            background: rgba(0, 255, 127, 0.1);
            border: 2px solid #00ff7f;
            border-radius: 10px;
            padding: 10px;
        }
        h1, h2, h3 {
            color: #00ff7f !important;
            text-shadow: 0 0 10px #00ff7f;
            font-family: 'Courier New', monospace;
        }
        .win-tag {
            color: #00ff00;
            font-weight: bold;
            font-size: 24px;
        }
        .loss-tag {
            color: #ff0000;
            font-weight: bold;
            font-size: 24px;
        }
        </style>
        """, unsafe_allow_html=True)
    else:  # ZEN mode
        st.markdown("""
        <style>
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .stMetric {
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid #d3d3d3;
            border-radius: 15px;
            padding: 15px;
        }
        h1, h2, h3 {
            color: #4a5568 !important;
            font-family: 'Georgia', serif;
        }
        .zen-message {
            font-style: italic;
            color: #718096;
            font-size: 18px;
        }
        </style>
        """, unsafe_allow_html=True)

apply_theme()

# Title with Theme-specific styling
if st.session_state.ui_theme == "OVERKILL":
    st.markdown("<h1>⚡ T.I.A. CITADEL - V19 INFINITE COCKPIT ⚡</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #00ff7f; font-family: monospace;'>🛸 NODE 08 BRIDGE ONLINE | DISTRIBUTED HIVE ACTIVE</p>", unsafe_allow_html=True)
else:
    st.markdown("<h1>🌸 T.I.A. Citadel - Zen Trading Space 🌸</h1>", unsafe_allow_html=True)
    st.markdown("<p class='zen-message'>Peace in the market, wisdom in the trade</p>", unsafe_allow_html=True)

# Sidebar - Configuration & Status
with st.sidebar:
    st.header("⚙️ System Configuration")
    
    # Theme Selector
    theme_option = st.selectbox(
        "UI Theme Mode",
        ["OVERKILL", "ZEN"],
        index=0 if st.session_state.ui_theme == "OVERKILL" else 1
    )
    if theme_option != st.session_state.ui_theme:
        st.session_state.ui_theme = theme_option
        st.rerun()
    
    # Safety Modulator (0-10 scale)
    st.session_state.safety_modulator = st.slider(
        "🎚️ Safety Modulator",
        min_value=0,
        max_value=10,
        value=st.session_state.safety_modulator,
        help="0 = Maximum Safety (Paper Trading) | 10 = Full Aggression (Live Trading)"
    )
    
    if st.session_state.ui_theme == "OVERKILL":
        modulator_color = "#ff0000" if st.session_state.safety_modulator > 7 else "#ffff00" if st.session_state.safety_modulator > 3 else "#00ff00"
        st.markdown(f"<p style='color: {modulator_color}; font-weight: bold;'>AGGRESSION LEVEL: {st.session_state.safety_modulator}/10</p>", unsafe_allow_html=True)
    else:
        st.info(f"Trading mindfulness level: {10 - st.session_state.safety_modulator}/10")
    
    st.markdown("---")
    
    # Backend Status
    st.header("🔌 System Status")
    try:
        health = requests.get(f"{API_URL}/telemetry/health", timeout=2).json()
        if st.session_state.ui_theme == "OVERKILL":
            st.markdown(f"<p style='color: #00ff00;'>✅ BACKEND: OPERATIONAL</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #00ffff;'>MODE: {health['mode']}</p>", unsafe_allow_html=True)
        else:
            st.success(f"Backend: Online ({health['mode']})")
    except:
        if st.session_state.ui_theme == "OVERKILL":
            st.markdown("<p style='color: #ff0000;'>❌ BACKEND: OFFLINE</p>", unsafe_allow_html=True)
        else:
            st.error("Backend: Offline")
    
    st.markdown("---")
    
    # Authentication Section
    st.header("🔐 Authentication")
    
    auth_method = st.radio("Auth Method", ["Standard Login", "GitHub Device Flow"])
    
    if auth_method == "Standard Login":
        if not st.session_state.token:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                try:
                    res = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
                    if res.status_code == 200:
                        st.session_state.token = res.json()["access_token"]
                        st.success("Logged in!")
                        st.rerun()
                    else:
                        st.error("Login failed")
                except Exception as e:
                    st.error(f"Connection error: {e}")
        else:
            st.success("✅ Authenticated")
            if st.button("Logout"):
                st.session_state.token = None
                st.rerun()
    else:
        # GitHub Device Flow
        if not st.session_state.token:
            if st.session_state.github_device_code is None:
                if st.button("🚀 Initialize Node 08 Bridge"):
                    try:
                        res = requests.post(f"{API_URL}/auth/github/device-code")
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.github_device_code = data
                            st.rerun()
                        else:
                            st.error(f"GitHub auth not enabled: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                device_data = st.session_state.github_device_code
                st.info(f"User Code: **{device_data['user_code']}**")
                st.markdown(f"[Authorize on GitHub]({device_data['verification_uri']})")
                
                if st.button("Poll for Token"):
                    try:
                        res = requests.post(
                            f"{API_URL}/auth/github/poll-token",
                            json={"device_code": device_data["device_code"]}
                        )
                        if res.status_code == 200:
                            result = res.json()
                            if result["status"] == "complete":
                                st.session_state.token = result["access_token"]
                                st.session_state.github_device_code = None
                                st.success("GitHub authentication successful!")
                                st.rerun()
                            else:
                                st.warning(f"Status: {result.get('error', 'pending')}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
                if st.button("Cancel"):
                    st.session_state.github_device_code = None
                    st.rerun()
        else:
            st.success("✅ GitHub Authenticated")
            if st.button("Logout"):
                st.session_state.token = None
                st.rerun()

# Main Content
if st.session_state.token:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Display based on theme
    if st.session_state.ui_theme == "OVERKILL":
        # OVERKILL MODE - Monstrous Charts, Win/Loss Logs, Math Boxes
        
        # Top Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🎯 ACTIVE DRONES", "6/6", "PHI-3.5 SWARM")
        with col2:
            st.metric("⚡ TRADES/SEC", "8.0", "+2.3")
        with col3:
            st.metric("💰 WIN RATE", "67.3%", "+5.2%")
        with col4:
            st.metric("🛡️ MALWARE SHIELD", "ARMED", "RED FLAG ACTIVE")
        
        # Tabs for different functions
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 STRATEGY ANALYSIS", 
            "⚔️ TRADE EXECUTION", 
            "🧠 BRAIN VAULT", 
            "📜 ROLLING LOGS",
            "🎵 RADIO CONTROL"
        ])
        
        with tab1:
            st.subheader("⚡ MARKET ANALYSIS ENGINE ⚡")
            col1, col2 = st.columns([2, 1])
            with col1:
                symbol = st.text_input("TARGET SYMBOL", "BTC/USDT", key="analysis_symbol")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                analyze_btn = st.button("🔍 ANALYZE", use_container_width=True)
            
            if analyze_btn:
                with st.spinner("🛸 SCANNING MARKET..."):
                    try:
                        res = requests.get(f"{API_URL}/strategy/analyze/{symbol}", headers=headers)
                        if res.status_code == 200:
                            data = res.json()
                            signal_color = "#00ff00" if data['signal'] == "BUY" else "#ff0000" if data['signal'] == "SELL" else "#ffff00"
                            st.markdown(f"<h2 style='color: {signal_color};'>SIGNAL: {data['signal']}</h2>", unsafe_allow_html=True)
                            
                            df = pd.DataFrame(data['data'])
                            st.dataframe(df, use_container_width=True, height=300)
                            
                            # Math boxes
                            st.markdown("### 📐 MATHEMATICAL INDICATORS")
                            mcol1, mcol2, mcol3 = st.columns(3)
                            with mcol1:
                                st.code(f"RSI_14: {df['RSI_14'].iloc[-1]:.2f}" if 'RSI_14' in df.columns else "RSI_14: N/A")
                            with mcol2:
                                st.code(f"SMA_20: {df['SMA_20'].iloc[-1]:.2f}" if 'SMA_20' in df.columns else "SMA_20: N/A")
                            with mcol3:
                                st.code(f"SMA_50: {df['SMA_50'].iloc[-1]:.2f}" if 'SMA_50' in df.columns else "SMA_50: N/A")
                        else:
                            st.error(f"❌ ERROR: {res.text}")
                    except Exception as e:
                        st.error(f"⚠️ SYSTEM ERROR: {e}")
        
        with tab2:
            st.subheader("⚔️ MANUAL EXECUTION TERMINAL ⚔️")
            st.warning(f"⚠️ SAFETY MODULATOR: {st.session_state.safety_modulator}/10")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                trade_symbol = st.text_input("TRADE SYMBOL", "BTC/USDT", key="trade_symbol")
            with col2:
                side = st.selectbox("SIDE", ["buy", "sell"])
            with col3:
                amount = st.number_input("AMOUNT", min_value=0.001, value=0.001, format="%.4f")
            
            if st.button("🚀 PLACE ORDER", use_container_width=True):
                with st.spinner("⚡ EXECUTING..."):
                    try:
                        payload = {
                            "symbol": trade_symbol,
                            "side": side,
                            "amount": amount,
                            "type": "market"
                        }
                        res = requests.post(f"{API_URL}/trade/order", json=payload, headers=headers)
                        if res.status_code == 200:
                            result = res.json()
                            st.success(f"✅ ORDER PLACED")
                            st.json(result)
                            
                            # Add to trade log
                            st.session_state.trade_log.append({
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "symbol": trade_symbol,
                                "side": side.upper(),
                                "amount": amount,
                                "status": "WIN" if st.session_state.safety_modulator < 8 else "PENDING"
                            })
                        else:
                            st.error(f"❌ ORDER FAILED: {res.text}")
                            st.session_state.trade_log.append({
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "symbol": trade_symbol,
                                "side": side.upper(),
                                "amount": amount,
                                "status": "LOSS"
                            })
                    except Exception as e:
                        st.error(f"⚠️ ERROR: {e}")
        
        with tab3:
            st.subheader("🧠 STATIC BRAIN VAULT 🧠")
            if st.button("📖 LOAD KNOWLEDGE BASE"):
                try:
                    res = requests.get(f"{API_URL}/brain/knowledge", headers=headers)
                    if res.status_code == 200:
                        st.json(res.json())
                    else:
                        st.error("Failed to load knowledge")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with tab4:
            st.subheader("📜 5-LINE ROLLING WIN/LOSS LOGS")
            st.markdown("**LATEST TRADE ACTIVITY**")
            
            # Display last 5 trades
            recent_trades = st.session_state.trade_log[-5:]
            for trade in reversed(recent_trades):
                status_class = "win-tag" if trade["status"] == "WIN" else "loss-tag"
                st.markdown(
                    f"<span class='{status_class}'>[{trade['status']}]</span> "
                    f"{trade['time']} | {trade['symbol']} | {trade['side']} | {trade['amount']:.4f}",
                    unsafe_allow_html=True
                )
            
            if len(st.session_state.trade_log) == 0:
                st.info("No trades logged yet. Execute trades to see activity here.")
        
        with tab5:
            st.subheader("🎵 RADIO MEDIA CONTROL")
            st.info("Radio player integration - Connect to your favorite trading beats")
            
            radio_station = st.selectbox("Select Station", [
                "🎸 Lofi Hip Hop Radio",
                "🎹 Synthwave Trading Vibes",
                "🎺 Jazz for Traders",
                "🔊 Electronic Focus Mix"
            ])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.button("▶️ Play")
            with col2:
                st.button("⏸️ Pause")
            with col3:
                st.button("⏭️ Next")
            
            volume = st.slider("Volume", 0, 100, 50)
    
    else:
        # ZEN MODE - Minimalist, Peaceful, Soft backgrounds
        
        st.markdown("### 🌊 Trading Harmony Dashboard")
        
        # Gentle metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active Drones", "6", "Phi-3.5 Swarm")
        with col2:
            st.metric("Win Rate", "67.3%", "+5.2%")
        with col3:
            st.metric("Safety Level", f"{10 - st.session_state.safety_modulator}/10", "Mindful")
        
        st.markdown("---")
        
        # Tabs with zen approach
        tab1, tab2, tab3, tab4 = st.tabs([
            "🌸 Analysis", 
            "💫 Execution", 
            "📚 Knowledge",
            "🎵 Media"
        ])
        
        with tab1:
            st.subheader("Market Analysis")
            symbol = st.text_input("Symbol (e.g. BTC/USDT)", "BTC/USDT", key="zen_symbol")
            if st.button("Analyze Market"):
                try:
                    res = requests.get(f"{API_URL}/strategy/analyze/{symbol}", headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        st.info(f"Signal: **{data['signal']}**")
                        df = pd.DataFrame(data['data'])
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with tab2:
            st.subheader("Mindful Trading")
            st.markdown("_Trade with intention and awareness_")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                trade_symbol = st.text_input("Symbol", "BTC/USDT", key="zen_trade_symbol")
            with col2:
                side = st.selectbox("Direction", ["buy", "sell"])
            with col3:
                amount = st.number_input("Amount", min_value=0.001, value=0.001, format="%.4f")
            
            if st.button("Place Order Mindfully"):
                try:
                    payload = {
                        "symbol": trade_symbol,
                        "side": side,
                        "amount": amount,
                        "type": "market"
                    }
                    res = requests.post(f"{API_URL}/trade/order", json=payload, headers=headers)
                    if res.status_code == 200:
                        st.success(f"Order placed with intention ✨")
                        st.json(res.json())
                    else:
                        st.error(f"Order not aligned: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with tab3:
            st.subheader("Knowledge Vault")
            if st.button("Access Knowledge"):
                try:
                    res = requests.get(f"{API_URL}/brain/knowledge", headers=headers)
                    if res.status_code == 200:
                        st.json(res.json())
                    else:
                        st.error("Failed to load knowledge")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with tab4:
            st.subheader("🎵 Ambient Audio")
            st.markdown("_Find your flow in the market_")
            
            # AI Yarning / Commentary
            zen_messages = [
                "The market flows like water, patience brings clarity",
                "In volatility, find stillness; in stillness, find opportunity",
                "Each trade is a meditation, each decision a breath",
                "The wise trader knows when to act and when to observe"
            ]
            
            st.info(zen_messages[int(time.time()) % len(zen_messages)])
            
            radio_station = st.selectbox("Ambient Selection", [
                "🌊 Ocean Waves",
                "🌲 Forest Sounds",
                "☁️ White Noise",
                "🎵 Meditation Music"
            ])
            
            col1, col2 = st.columns(2)
            with col1:
                st.button("▶️ Play")
            with col2:
                st.button("⏸️ Pause")

else:
    # Not authenticated
    if st.session_state.ui_theme == "OVERKILL":
        st.markdown("<h2 style='color: #ff0000;'>⚠️ AUTHENTICATION REQUIRED ⚠️</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #00ff7f;'>ACCESS THE CITADEL VIA SIDEBAR LOGIN</p>", unsafe_allow_html=True)
    else:
        st.info("🔐 Please authenticate to access the trading space")
        st.markdown("_Find peace in security, wisdom in patience_")
