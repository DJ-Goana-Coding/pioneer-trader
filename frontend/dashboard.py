
import streamlit as st
import requests
import pandas as pd
import time
import plotly.graph_objects as go

# --- CONFIG ---
API_URL = "http://localhost:8000"
st.set_page_config(page_title="T.I.A. Command Center", layout="wide", page_icon="🦎")

# --- STYLING (Matrix Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00FF00; font-family: 'Courier New', monospace; }
    .stButton>button { border: 1px solid #00FF00; color: #00FF00; background: transparent; }
    .stButton>button:hover { background: #00FF00; color: #000000; }
    div[data-testid="stMetricValue"] { color: #00FF00; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🦎 T.I.A. TACTICAL CONSOLE")
    st.caption("Frankfurt Citadel // Vortex Engine V1")
with col2:
    st.image("https://img.icons8.com/color/96/matrix-desktop.png", width=60)

# --- API HANDLER ---
def get_status():
    try:
        r = requests.get(f"{API_URL}/engine/status", timeout=2)
        return r.json()
    except:
        return None

def toggle_engine(action):
    try:
        requests.post(f"{API_URL}/engine/{action}")
        st.toast(f"COMMAND SENT: {action.upper()}", icon="🚀")
        time.sleep(1)
        st.rerun()
    except:
        st.error("COMMS LINK FAILED")

# --- SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.header("🎮 MANUAL OVERRIDE")
    status = get_status()
    
    if status and status.get('active'):
        st.success("SYSTEM: ONLINE")
        if st.button("🛑 EMERGENCY STOP", use_container_width=True):
            toggle_engine("stop")
    else:
        st.warning("SYSTEM: OFFLINE")
        if st.button("🔥 IGNITE VORTEX", use_container_width=True):
            toggle_engine("start")
            
    st.divider()
    st.markdown("**STRATEGY OVERLAY**")
    st.checkbox("Show P25 Momentum", value=True)
    st.checkbox("Show Golden Cross", value=True)

# --- MAIN DISPLAY ---
# 1. Telemetry Strip
m1, m2, m3, m4 = st.columns(4)
if status:
    m1.metric("CYCLES", status.get('cycles_completed', 0))
    m2.metric("ACTIVE STRATEGIES", len(status.get('loaded_strategies', [])))
    m3.metric("WALLET (SIM)", "$1,000.00")
    m4.metric("LATENCY", "12ms")
else:
    st.error("⚠️ UNABLE TO CONNECT TO BACKEND API (Port 8000)")

# 2. Visualizer (The Chart)
st.divider()
st.subheader("📉 MARKET VORTEX VISUALIZER")

# Mock Data for Chart
chart_data = pd.DataFrame({
    'Time': pd.date_range(start='now', periods=50, freq='1min'),
    'Price': [65000 + (i*10) + (i%5)*50 for i in range(50)],
    'EMA_50': [64900 + (i*8) for i in range(50)]
})

fig = go.Figure()
fig.add_trace(go.Candlestick(x=chart_data['Time'],
                open=chart_data['Price']-50, high=chart_data['Price']+100,
                low=chart_data['Price']-100, close=chart_data['Price'],
                name='BTC/USDT'))
fig.add_trace(go.Scatter(x=chart_data['Time'], y=chart_data['EMA_50'], line=dict(color='#00FF00', width=1), name='EMA 50'))

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#00FF00'),
    xaxis_rangeslider_visible=False,
    height=400,
    margin=dict(l=0, r=0, t=0, b=0)
)
st.plotly_chart(fig, use_container_width=True)

# 3. Live Logs
st.subheader("📠 TACTICAL LOGS")
with st.container(height=200):
    st.code("""
    [17:55:54] INFO: VORTEX | Cycle 1 Complete.
    [17:55:54] INFO: STRAT  | Trend_EMA_01 > HOLD (RSI 45)
    [17:55:54] INFO: STRAT  | MR_RSI_01    > BUY SIGNAL (RSI 28)
    [17:55:49] INFO: SYSTEM | Binder loaded 2 strategies.
    [17:55:49] INFO: SYSTEM | Vortex Engine Ignited.
    """, language="bash")
