import streamlit as st
import requests
import pandas as pd

# Config
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Pioneer-Admiral V1", layout="wide")

st.title("Pioneer-Admiral V1 Cockpit")

# Session State for Auth
if 'token' not in st.session_state:
    st.session_state.token = None

# Sidebar - Auth & Status
with st.sidebar:
    st.header("System Status")
    try:
        health = requests.get(f"{API_URL}/telemetry/health").json()
        st.success(f"Backend: Online ({health['mode']})")
    except:
        st.error("Backend: Offline")

    st.header("Authentication")
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
        st.info("Authenticated")
        if st.button("Logout"):
            st.session_state.token = None
            st.rerun()

# Main Content
if st.session_state.token:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Strategy Analysis", "Trade Execution", "Brain"])
    
    with tab1:
        st.subheader("Market Analysis")
        symbol = st.text_input("Symbol (e.g. BTC/USDT)", "BTC/USDT")
        if st.button("Analyze"):
            try:
                res = requests.get(f"{API_URL}/strategy/analyze/{symbol}", headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    st.write(f"Signal: **{data['signal']}**")
                    df = pd.DataFrame(data['data'])
                    st.dataframe(df)
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")

    with tab2:
        st.subheader("Manual Execution")
        col1, col2, col3 = st.columns(3)
        with col1:
            trade_symbol = st.text_input("Trade Symbol", "BTC/USDT")
        with col2:
            side = st.selectbox("Side", ["buy", "sell"])
        with col3:
            amount = st.number_input("Amount", min_value=0.001, value=0.001, format="%.4f")
            
        if st.button("Place Order"):
            try:
                payload = {
                    "symbol": trade_symbol,
                    "side": side,
                    "amount": amount,
                    "type": "market"
                }
                res = requests.post(f"{API_URL}/trade/order", json=payload, headers=headers)
                if res.status_code == 200:
                    st.success(f"Order Placed: {res.json()}")
                else:
                    st.error(f"Order Failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")

    with tab3:
        st.subheader("Static Brain")
        if st.button("Load Knowledge"):
            try:
                res = requests.get(f"{API_URL}/brain/knowledge", headers=headers)
                if res.status_code == 200:
                    st.json(res.json())
                else:
                    st.error("Failed to load knowledge")
            except Exception as e:
                st.error(f"Error: {e}")

else:
    st.warning("Please login to access the cockpit.")
