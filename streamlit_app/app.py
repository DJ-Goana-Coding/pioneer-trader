import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="Pioneer Trader", layout="wide")
BACKEND_URL = "http://localhost:8000"

st.title("Pioneer Trader — Frankfurt Cockpit")
st.markdown("**Status:** 🟢 Online | **Security:** 🔓 Open Mode")

# --- TELEMETRY LOOP ---
st.subheader("📡 Live Vortex Status")
if st.button("Refresh Telemetry"):
    try:
        r = requests.get(f"{BACKEND_URL}/telemetry", timeout=2)
        data = r.json()
        
        # Display Engine Status
        st.metric("Engine Status", data.get("status", "Unknown"))
        st.metric("Banked Profit", f"${data.get('banked_profit', 0.0)}")
        
        # Display Slots Table
        slots = data.get("slots", [])
        if slots:
            df = pd.DataFrame(slots)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No Slots Found")
            
    except Exception as e:
        st.error(f"Connection Error: {e}")

# --- CONTROLS ---
col1, col2 = st.columns(2)
with col1:
    st.info("🧠 Strategy Control")
    if st.button("Reload T.I.A. Logic"):
        requests.post(f"{BACKEND_URL}/strategy/reload", json={"strategy": "vortex_v1"})
        st.success("Signal Sent")

with col2:
    st.info("⚡ Emergency")
    if st.button("STOP ENGINE"):
        st.error("Stop Signal Sent (Not Implemented yet)")
