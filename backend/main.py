@app.on_event("startup")
async def startup_event():
    """Starts the Vortex Engine on API Ignition"""
    global vortex
    try:
        # Import the hardened Berserker engine
        from backend.services.vortex import VortexBerserker
        vortex = VortexBerserker()
        
        # Engage Background Loop
        asyncio.create_task(vortex.start())
        logger.info("🏰 CITADEL: VortexBerserker Engaged")
    except Exception as e:
        logger.error(f"🚨 IGNITION FAILURE: {e}")

    return {"status": "Citadel Online", "engine": "Vortex V6.9 Berserker"}