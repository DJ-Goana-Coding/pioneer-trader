import subprocess
import time
import sys
from backend.core.logging_config import setup_logging

logger = setup_logging("run_app")

def main():
    logger.info("Starting Backend...")
    # Start FastAPI Backend in the background
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
    )
    
    # Wait a few seconds for backend to initialize
    time.sleep(5)
    
    logger.info("Starting Frontend...")
    # Start Streamlit Frontend in the foreground
    # We use sys.executable to ensure we use the same python environment
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "streamlit_app/app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
    )

    # If streamlit exits, kill backend
    backend.terminate()

if __name__ == "__main__":
    main()
