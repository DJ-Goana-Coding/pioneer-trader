
# 🏛️ DEVELOPER HANDOVER: THE FRANKFURT CITADEL
**Status:** Operational (V2 Monolith)
**Architect:** T.I.A. / Quantum Goanna
**Updated:** 2026-01-15

## 📍 SYSTEM MISSION
This is a high-frequency, multi-personality crypto trading system. It is designed to run **7 parallel slots** of capital ($10.50 each) targeting volatility in assets like XRP, DASH, and SOL.

## 🏗️ THE STACK (Hybrid Architecture)
* **Backend:** Python 3.11 / FastAPI (Port 8000). Handles the 'Vortex Engine' and 'Skin-Walker' logic.
* **Frontend:** Streamlit (Port 10000) for internal telemetry + Next.js (Vercel) for the public cockpit.
* **Database:** File-based 'Encyclopedia' (JSON) for Forever Learning.
* **Hosting:** Render (Frankfurt) for the main brain; Hugging Face (Docker) as redundant backup.

## ⚙️ CORE LOGIC: "THE HAMMER"
The strategy is located in `backend/services/strategies.py`. It uses `pandas_ta` for:
1. **P25 Momentum:** RSI < 30 (Oversold) + EMA_50 trend confirmation.
2. **Golden Cross:** SMA 50/200 cross for macro trend surfing.
3. **Worker Loop:** `vortex.py` runs an async heartbeat every 10 seconds to scan for entries across 7 slots.

## 📂 DIRECTORY MAP

### Infrastructure
* ✅ `start.sh`
* ✅ `requirements.txt`
* ✅ `render.yaml`
* ✅ `Dockerfile`

### The Brain
* ✅ `backend/main.py`
* ✅ `backend/services/brain.py`

### The Muscle
* ✅ `backend/services/vortex.py`
* ✅ `backend/services/strategies.py`

### The Face
* ✅ `streamlit_app/app.py`
* ❌ `frontend/pages/index.js`

## 🛠️ HOW TO WORK ON THIS
1. **To Repair:** Re-run the 'God Script' to restore core file integrity.
2. **To Scale:** Edit `VortexEngine` in `vortex.py` to increase slot count beyond 7.
3. **To Morph:** Add new personas to `backend/core/personas.py`. Triggers are automatic based on chat keywords.

---
*Note: This system is built for Darrell. Strict "No Placeholder" policy is active.*
