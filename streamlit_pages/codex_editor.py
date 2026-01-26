
import streamlit as st
import json
import os

CODEX_PATH = "registry/codex.json"
st.set_page_config(layout="wide", page_title="Citadel Codex Editor")

st.title("🎛️ T.I.A. Codex Editor")

if not os.path.exists(CODEX_PATH):
    st.error(f"Codex not found at {CODEX_PATH}")
    st.stop()

with open(CODEX_PATH, "r") as f:
    data = json.load(f)

# Simple View for now
st.json(data)
st.warning("⚠️ Edit Mode locked. Deploy to Render to unlock write-access.")
