if __name__ == "__main__":
    # Render provides a $PORT env var. 
    # We default to 10000 if not found (Render's standard)
    port = int(os.environ.get("PORT", 10000)) 
    
    print(f"🚀 CITADEL IGNITION ON PORT {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
