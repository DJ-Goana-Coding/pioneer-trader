#!/bin/bash
echo "🛰️ T.I.A. COMMAND: IGNITING VORTEX ENGINE..."
export PORT=${PORT:-10000}
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT