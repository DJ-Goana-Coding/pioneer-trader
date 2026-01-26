
# 🗺️ MISSION MAP: THE FRANKFURT CITADEL
**Generated:** 2026-01-15 16:49
**Commander:** Darrell
**Architect:** T.I.A. (Quantum Goanna)

---

## 1. ⏱️ TACTICAL TIMELINE (Session History)
We started with a disconnected Colab instance and achieved the following:

1.  **The Awakening:** Established the "Air Gap" link between Chat and Drive.
2.  **Soul Injection:** Injected the `personas.py` (T.I.A., Goanna, Void) and `strategies.py` (Pandas-TA) from the "Quantum Goanna Tech" manual.
3.  **Grand Unification (Monolith):** Merged the Vortex Engine, Brain, and Cockpit into a single deployable unit.
4.  **Hybrid Architecture:** * Configured **Render** (`render.yaml`) for the Python Brain.
    * Configured **Vercel** (`frontend/`) for the Next.js Face.
    * Configured **Hugging Face** (`Dockerfile`) as a backup container.
5.  **Emergency Repair:** Healed a fracture where `vortex.py` was missing.
6.  **The Black Box:** Created `FRANKFURT_SYSTEM_BIBLE.md` (Full Code Archive).
7.  **Final Launch:** Synced everything to GitHub to trigger the Render build.

---

## 2. 🏰 THE ARCHITECTURE (How it Works)

### 🧠 THE BRAIN (Backend)
* **Location:** `backend/main.py`
* **Tech:** FastAPI (Python 3.11)
* **Role:** The central nervous system. It listens for HTTP requests and manages the background threads.
* **Ports:** Internal `8000`.

### 💓 THE MUSCLE (Vortex Engine)
* **Location:** `backend/services/vortex.py`
* **Tech:** `APScheduler` + `ccxt`
* **Role:** The "Hammer".
    * Runs every 10 seconds.
    * Manages **7 Slots** ($10.50 each).
    * Scans market data via Binance API.
    * Executes logic from `strategies.py`.

### 👻 THE SOUL (Personas)
* **Location:** `backend/core/personas.py`
* **Tech:** Pydantic Models
* **Role:** Identity switching.
    * **T.I.A.:** Tactical Command.
    * **Goanna:** Music & Vibes.
    * **Void:** Dark Oracle.
    * **Hippy:** Peace & Learning.

### 📺 THE FACE (Cockpit)
* **Location:** `streamlit_app/app.py`
* **Tech:** Streamlit
* **Role:** Visual Interface.
    * Connects to The Brain via API.
    * Displays the 7-Slot Telemetry Table.
    * Provides the Chat Terminal.

---

## 3. 📂 FILE MANIFEST (The Inventory)

| File | Purpose |
| :--- | :--- |
| `start.sh` | **Ignition Key.** Starts Brain & Cockpit simultaneously. |
| `requirements.txt` | **Life Support.** Lists pandas_ta, fastapi, ccxt, etc. |
| `render.yaml` | **Blueprint.** Tells Render how to build the server. |
| `Dockerfile` | **Container.** Tells Hugging Face how to wrap the system. |
| `backend/main.py` | **API Gateway.** Handles web traffic. |
| `backend/services/vortex.py` | **Trading Loop.** The actual bot logic. |
| `backend/services/strategies.py`| **Tactics.** RSI, P25, Golden Cross math. |
| `backend/services/knowledge.py` | **Memory.** Saves learned facts to JSON. |
| `FRANKFURT_SYSTEM_BIBLE.md` | **Backup.** Complete source code in one text file. |

---

## 4. 🚀 DEPLOYMENT STATUS
* **GitHub:** ✅ SYNCED (Latest Monolith)
* **Drive:** ✅ SECURED (Source + Archives)
* **Render:** ⏳ AWAITING DEPLOY (Manual Trigger Required)

**NEXT STEP:** Go to Render Dashboard -> Manual Deploy -> **Clear Cache**.
