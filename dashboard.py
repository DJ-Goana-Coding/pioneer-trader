import streamlit as st
import requests
import os

st.set_page_config(page_title="T.I.A. Command", page_icon="🐊")
st.title("🛡️ T.I.A. Mobile Command")

API_URL = os.getenv("API_URL", "https://pioneer-trader.onrender.com") # Update with your Render URL
AUTH_TOKEN = os.getenv("KILL_AUTH_TOKEN")

if st.button("🔄 Refresh Status"):
    try:
        res = requests.get(f"{API_URL}/health").json()
        st.success(f"Status: {res['bot_data']['status']}")
        st.json(res)
    except:
        st.error("Could not reach the Pioneer Node.")

st.divider()

if st.button("🚨 TRIGGER OMEGA-STOP", type="primary"):
    headers = {"auth": AUTH_TOKEN}
    try:
        res = requests.post(f"{API_URL}/omega-stop", headers=headers)
        st.warning(res.json().get("message"))
    except:
        st.error("Shutdown command failed.")