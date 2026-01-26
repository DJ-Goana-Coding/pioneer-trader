
import subprocess
import time
import os
import sys
import threading

def stream_logs(process, name):
    for line in iter(process.stdout.readline, b''):
        print(f"[{name}] {line.decode().strip()}")

def boot():
    print("🔌 KILLING ZOMBIE PROCESSES...")
    os.system("pkill -f uvicorn")
    os.system("pkill -f streamlit")

    print("🧠 IGNITING VORTEX BRAIN (FastAPI :8000)...")
    backend = subprocess.Popen(
        ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    # Thread to read backend logs
    t_back = threading.Thread(target=stream_logs, args=(backend, "BRAIN"))
    t_back.daemon = True
    t_back.start()

    time.sleep(5) # Give the Brain a moment to wake up

    print("🦎 SUMMONING COMMAND CONSOLE (Streamlit :8501)...")
    frontend = subprocess.Popen(
        ["streamlit", "run", "frontend/dashboard.py", "--server.port", "8501", "--server.headless", "true"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    # Thread to read frontend logs
    t_front = threading.Thread(target=stream_logs, args=(frontend, "FACE "))
    t_front.daemon = True
    t_front.start()

    print("\n✅ CITADEL IS ONLINE.")
    print("   - Backend Logic: http://localhost:8000")
    print("   - Dashboard UI:  http://localhost:8501")
    print("   - Logs are streaming below... (Press Stop to kill)\n")

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n🛑 SHUTDOWN SEQUENCE INITIATED...")
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    boot()
