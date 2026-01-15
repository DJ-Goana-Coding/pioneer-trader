import streamlit as st
import requests
import time

st.set_page_config(page_title="Pioneer Trader — Frankfurt Cockpit", layout="wide")
st.title("Pioneer Trader — Frankfurt Cockpit")
backend_base = "http://localhost:8000"

st.subheader("🗺️ Routing Visualizer")
st.markdown("**UI Port:** 10000 (Public) | **Backend:** 8000 (Internal)")

col1, col2 = st.columns(2)
with col1:
    st.info("📡 Telemetry")
    if st.button("Fetch Telemetry"):
        try:
            st.json(requests.get(f"{backend_base}/telemetry", timeout=2).json())
        except Exception as e: st.error(str(e))

with col2:
    st.info("🧠 Strategy Control")
    strat = st.text_input("Strategy", "simple_rsi")
    if st.button("Hot Reload"):
        try:
            st.json(requests.post(f"{backend_base}/strategy/reload", json={"strategy": strat}, timeout=2).json())
        except Exception as e: st.error(str(e))
