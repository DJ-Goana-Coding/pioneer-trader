import streamlit as st
import requests
import pandas as pd
st.set_page_config(page_title="Pioneer Trader", layout="wide")
API = "http://localhost:8000"
st.title("Pioneer Trader — Frankfurt Citadel")
col1, col2 = st.columns(2)
with col1:
    st.subheader("📡 Vortex Workers")
    if st.button("Refresh Telemetry"):
        try:
            data = requests.get(f"{API}/telemetry", timeout=3).json()
            st.metric("System Status", data["status"])
            st.dataframe(pd.DataFrame(data["slots"]), use_container_width=True)
        except: st.error("Backend Offline")
with col2:
    st.subheader("💬 T.I.A. Command")
    user_input = st.text_input("Execute Order / Switch Persona")
    if st.button("Send Command"):
        try:
            resp = requests.post(f"{API}/chat", json={"message": user_input}).json()
            st.success(resp["msg"])
            st.caption(f"Identity: {resp.get('persona')}")
        except: st.error("Comms Failure")
