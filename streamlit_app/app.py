import streamlit as st
import requests
import time

st.set_page_config(page_title="Pioneer Trader", layout="wide")
BACKEND_URL = "http://localhost:8000"

# --- SESSION STATE ---
if "token" not in st.session_state:
    st.session_state.token = None

# --- LOGIN SCREEN ---
def login_screen():
    st.title("🛡️ Pioneer-Admiral Login")
    with st.form("login"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.form_submit_button("Access Citadel"):
            try:
                r = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json={"username": user, "password": pwd},
                    timeout=5
                )
                if r.status_code == 200:
                    st.session_state.token = r.json()["access_token"]
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
            except Exception as e:
                st.error(f"Connection Failed: {e}")

# --- DASHBOARD (Protected) ---
def dashboard():
    st.sidebar.success("Logged In")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.rerun()

    # The Token Header for all requests
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    st.title("Pioneer Trader — Frankfurt Cockpit")
    st.markdown("**UI Port:** 10000 (Public) | **Backend:** 8000 (Protected)")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📡 Telemetry")
        if st.button("Fetch Data"):
            try:
                r = requests.get(f"{BACKEND_URL}/telemetry", headers=headers, timeout=2)
                if r.status_code == 200:
                    st.json(r.json())
                else:
                    st.error(f"Access Denied: {r.status_code}")
            except Exception as e: st.error(str(e))

    with col2:
        st.subheader("🧠 Strategy Ops")
        strat = st.text_input("Strategy", "simple_rsi")
        if st.button("Hot Reload"):
            try:
                r = requests.post(f"{BACKEND_URL}/strategy/reload", json={"strategy": strat}, headers=headers, timeout=2)
                if r.status_code == 200:
                    st.json(r.json())
                else:
                    st.error(f"Access Denied: {r.status_code}")
            except Exception as e: st.error(str(e))

# --- ROUTER ---
if st.session_state.token:
    dashboard()
else:
    login_screen()
