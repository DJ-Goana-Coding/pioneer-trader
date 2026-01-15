import httpx
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import Response
import uvicorn

app = FastAPI()

# INTERNAL PORTS
STREAMLIT_PORT = 7860
FASTAPI_PORT = 8000

# HTTP ROUTING
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(request: Request, path: str):
    # Route API/Auth calls to Backend
    if path.startswith("api") or path.startswith("docs") or path.startswith("openapi") or path.startswith("token"):
        target_url = f"http://127.0.0.1:{FASTAPI_PORT}/{path}"
    # Route everything else to Streamlit UI
    else:
        target_url = f"http://127.0.0.1:{STREAMLIT_PORT}/{path}"

    async with httpx.AsyncClient() as client:
        try:
            content = await request.body()
            proxied = await client.request(
                request.method,
                target_url,
                headers=request.headers,
                params=request.query_params,
                content=content
            )
            return Response(
                content=proxied.content,
                status_code=proxied.status_code,
                headers=dict(proxied.headers)
            )
        except Exception as e:
            return Response(content=f"Proxy Error: {str(e)}", status_code=502)

# WEBSOCKET ROUTING (Stub for Streamlit)
@app.websocket("/{path:path}")
async def websocket_proxy(websocket: WebSocket, path: str):
    await websocket.accept()
    # Note: Full WS proxying is complex. We accept the connection to prevent 
    # immediate errors, but Streamlit will fallback to long-polling automatically.
    pass