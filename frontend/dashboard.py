
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

def get_cockpit_status():
    try:
        r = requests.get(f"{API_URL}/cockpit/status", timeout=2)
        return r.json()
    except:
        return None

def authorize_admiral(force=False):
    try:
        r = requests.post(f"{API_URL}/cockpit/authorize", json={"force": force}, timeout=2)
        return r.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

def revoke_admiral(reason="Manual revocation"):
    try:
        r = requests.post(f"{API_URL}/cockpit/revoke", json={"reason": reason}, timeout=2)
        return r.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

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
    
    # --- T.I.A. COCKPIT CONTROLS ---
    st.header("🦎 T.I.A. COCKPIT")
    cockpit_status = get_cockpit_status()
    
    if cockpit_status:
        # T.I.A. Status
        tia = cockpit_status.get("tia", {})
        risk_level = tia.get("risk_level", "UNKNOWN")
        confidence = tia.get("confidence", 0) * 100
        
        # Risk level indicator
        if risk_level == "LOW":
            st.success(f"🟢 RISK: {risk_level}")
        elif risk_level == "MEDIUM":
            st.warning(f"🟡 RISK: {risk_level}")
        else:
            st.error(f"🔴 RISK: {risk_level}")
        
        st.caption(f"Confidence: {confidence:.0f}%")
        st.caption(tia.get("message", ""))
        
        st.divider()
        
        # Admiral Authorization Status
        auth = cockpit_status.get("authorization", {})
        is_authorized = auth.get("authorized", False)
        
        if is_authorized:
            st.success("⚔️ ADMIRAL: AUTHORIZED")
            admiral_info = auth.get("admiral", {})
            enabled_count = len(admiral_info.get("enabled_capabilities", []))
            st.caption(f"Premium Capabilities: {enabled_count}")
            
            # Revoke button
            if st.button("🔒 REVOKE ACCESS", use_container_width=True):
                result = revoke_admiral()
                if result.get("success"):
                    st.toast("Admiral access REVOKED", icon="🔒")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Failed: {result.get('message')}")
        else:
            st.warning("⚔️ ADMIRAL: RESTRICTED")
            st.caption("Base capabilities only")
            
            # Authorize button
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ AUTHORIZE", use_container_width=True):
                    result = authorize_admiral()
                    if result.get("success"):
                        st.toast("Admiral AUTHORIZED", icon="✅")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Denied: {result.get('message')}")
            with col2:
                if st.button("⚠️ FORCE", use_container_width=True):
                    result = authorize_admiral(force=True)
                    if result.get("success"):
                        st.toast("Admiral FORCED AUTH", icon="⚠️")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Failed: {result.get('message')}")
    else:
        st.error("Cockpit Offline")
            
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

# 1.5. T.I.A. Cockpit Status Banner
cockpit_status = get_cockpit_status()
if cockpit_status:
    st.divider()
    st.subheader("🌉 T.I.A. → ADMIRAL BRIDGE")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tia = cockpit_status.get("tia", {})
        risk_level = tia.get("risk_level", "UNKNOWN")
        
        if risk_level == "LOW":
            st.metric("T.I.A. Risk Level", "🟢 LOW", help="System posture excellent")
        elif risk_level == "MEDIUM":
            st.metric("T.I.A. Risk Level", "🟡 MEDIUM", help="Elevated risk detected")
        else:
            st.metric("T.I.A. Risk Level", "🔴 HIGH", help="HIGH RISK: Defensive posture")
    
    with col2:
        auth = cockpit_status.get("authorization", {})
        is_authorized = auth.get("authorized", False)
        
        if is_authorized:
            st.metric("Admiral Status", "⚔️ AUTHORIZED", help="Premium capabilities enabled")
        else:
            st.metric("Admiral Status", "🔒 RESTRICTED", help="Base capabilities only")
    
    with col3:
        if is_authorized:
            admiral_info = auth.get("admiral", {})
            premium_caps = admiral_info.get("premium_capabilities", [])
            st.metric("Premium Features", len(premium_caps), help="Total premium capabilities")
        else:
            st.metric("Premium Features", "0", delta="Locked", delta_color="off")
    
    # Show premium capabilities if authorized
    if is_authorized:
        with st.expander("⚔️ PREMIUM CAPABILITIES", expanded=False):
            admiral_info = auth.get("admiral", {})
            enabled_caps = admiral_info.get("enabled_capabilities", [])
            
            cap_cols = st.columns(3)
            for idx, cap in enumerate(enabled_caps):
                with cap_cols[idx % 3]:
                    # Format capability name
                    display_name = cap.replace("_", " ").title()
                    st.markdown(f"✅ **{display_name}**")


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
