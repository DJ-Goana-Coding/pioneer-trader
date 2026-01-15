#!/usr/bin/env bash
set -e

echo '🚀 STARTING FRANKFURT STACK...'

# 1. Start Backend (Port 8000) in Background
echo '🧠 Starting Backend on 8000...'
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# 2. Start Streamlit (Port 7860) in Background
echo '📺 Starting Cockpit on 7860...'
streamlit run streamlit_app/app.py --server.port 7860 --server.address 0.0.0.0 &

# 3. Start Proxy (Port 10000) in FOREGROUND
# This keeps the container alive and answers Render's health check
echo 'TGATE Starting Proxy on 10000...'
python backend/proxy.py
