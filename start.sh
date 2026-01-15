#!/bin/bash

echo "🚀 Starting Pioneer-Admiral Systems..."

# 1. Start Backend Brain (Background)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
echo "✅ Backend started on port 8000"

# 2. Start Streamlit Faceplate (Background)
# We add --server.baseUrlPath="" to ensure it handles root correctly
streamlit run streamlit_app/app.py --server.port=7860 --server.address=0.0.0.0 --server.headless=true &
echo "✅ Streamlit started on port 7860"

# 3. Start Tiny Proxy (Foreground - Keeps Container Alive)
echo "🛡️ Starting Proxy on port 10000..."
uvicorn backend.proxy:app --host 0.0.0.0 --port 10000