import streamlit as st
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURATION & AGGRESSION ---
STAKE_MIN = 5.00
BOT_ALLOWANCE_LIMIT = 50.00  # Hard capped start
# Total Scalpers = (Garage Bays * Slots) = (4 * 45) = 180 Scalpers available

# --- STYLING: THE "OVERKILL" TERMINAL ---
st.markdown("""
    <style>
    .trade-row { font-family: 'Courier New', monospace; font-size: 14px; padding: 4px; border-bottom: 1px solid #333; }
    .ball { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .green-ball { background-color: #00ff00; box-shadow: 0 0 10px #00ff00; }
    .red-ball { background-color: #ff0000; box-shadow: 0 0 10px #ff0000; }
    .yellow-ball { background-color: #ffff00; box-shadow: 0 0 10px #ffff00; }
    .white-ball { background-color: #ffffff; }
    .profit { color: #00ff00; font-weight: bold; }
    .loss { color: #ff0000; font-weight: bold; }
    .neutral { color: #ffff00; }
    </style>
""", unsafe_allow_html=True)

# --- SOVEREIGN CAPITAL MONITOR ---
st.title("🏰 FRANKFURT CITADEL | V19-G")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric("TOTAL WALLET", "$80.25", delta="+$1.12")
with col_b:
    st.metric("BOT ALLOWANCE", f"${BOT_ALLOWANCE_LIMIT:.2f}", delta="- Hard Capped")
with col_c:
    st.metric("ACTIVE SCALPERS", "180", delta="Aggression: 10/10", delta_color="inverse")

st.divider()

# --- THE ROLLING TRADE FEED (5-8 LINES) ---
st.subheader("📡 LIVE VORTEX STREAM")

# Mock data for demonstration - in production, this pulls from st.session_state.live_trades
trades = [
    {"type": "sell", "coin": "SOL", "qty": "0.12", "price": "145.20", "pl": "+$2.40", "status": "green"},
    {"type": "buy", "coin": "AVAX", "qty": "1.50", "price": "34.10", "pl": "---", "status": "yellow"},
    {"type": "sell", "coin": "PEPE", "qty": "1.2M", "price": "0.00001", "pl": "-$0.50", "status": "red"},
    {"type": "hold", "coin": "SUI", "qty": "10.0", "price": "1.12", "pl": "+$0.02", "status": "white"},
    {"type": "buy", "coin": "HBAR", "qty": "100.0", "price": "0.07", "pl": "---", "status": "yellow"},
]

for t in trades:
    ball_class = f"{t['status']}-ball"
    pl_class = "profit" if "+" in t['pl'] else ("loss" if "-" in t['pl'] else "neutral")
    
    st.markdown(f"""
        <div class="trade-row">
            <span class="ball {ball_class}"></span>
            <b>{t['coin']}</b> | {t['type'].upper()} | Qty: {t['qty']} | Price: ${t['price']} | 
            <span class="{pl_class}">P/L: {t['pl']}</span>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# --- ACTIVE SLOTS MONITOR ---
st.subheader("🎰 ENGINE BAYS: 45 SLOTS")
slot_data = {
    "Slot #": range(1, 7),
    "Coin": ["SOL", "AVAX", "SUI", "PEPE", "HBAR", "WLFI"],
    "Buy Price": ["$142.80", "$34.10", "$1.10", "$0.00001", "$0.07", "$0.50"],
    "Current": ["$145.20", "$34.05", "$1.12", "$0.000009", "$0.07", "$0.50"],
    "Trend": ["🟢 +1.6%", "🟡 -0.1%", "🟢 +1.8%", "🔴 -10%", "⚪ 0.0%", "⚪ 0.0%"]
}
st.table(pd.DataFrame(slot_data))

# --- AGGRESSION CONTROL ---
if st.sidebar.button("🔥 RELEASE ALL SCALPERS (10/10)"):
    st.sidebar.error("SYSTEM BREACH: MAXIMUM AGGRESSION ENGAGED")
    # Trigger your Airgap/Firestone override here
