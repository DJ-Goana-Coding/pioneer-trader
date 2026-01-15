#!/usr/bin/env bash
set -e
echo '🚀 STARTING FRANKFURT CITADEL...'
# Start Brain (Internal Port 8000)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
sleep 5
# Start Face (Public Port 7860 for Hugging Face / 10000 for Render)
streamlit run streamlit_app/app.py --server.port 7860 --server.address 0.0.0.0