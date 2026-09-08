
import uvicorn
from fastapi import FastAPI
import os
from backend.core.logging_config import setup_logging

logger = setup_logging("proxy")

# Define the Proxy App
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Frankfurt Citadel Proxy Online", "status": "Green"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # Bind explicitly to Port 7860 (HuggingFace Spaces Standard)
    logger.info("🚀 PROXY STARTING ON PORT 7860")
    uvicorn.run(app, host="0.0.0.0", port=7860)
