
import uvicorn
from fastapi import FastAPI
import os

# Define the Proxy App
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Frankfurt Citadel Proxy Online", "status": "Green"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # Bind explicitly to Port 10000 (Render's Requirement)
    print("🚀 PROXY STARTING ON PORT 10000")
    uvicorn.run(app, host="0.0.0.0", port=10000)
