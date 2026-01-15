#!/usr/bin/env bash
set -e
echo '🚀 STARTING FRANKFURT STACK (DIRECT UI MODE)...'
echo '🧠 Starting Backend on 8000...'
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
sleep 5
echo '📺 Starting Cockpit on 10000...'
streamlit run streamlit_app/app.py --server.port 10000 --server.address 0.0.0.0
