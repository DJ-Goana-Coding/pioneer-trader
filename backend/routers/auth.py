from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.core.security import create_access_token, get_current_user, verify_password, get_password_hash
from backend.core.config import settings
from pydantic import BaseModel
import httpx
import secrets

router = APIRouter(prefix="/auth", tags=["auth"])

# Mock user database for simplicity. In production, use a real DB.
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("admin123"), # Default password
        "disabled": False,
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}

# GitHub Device Flow Authentication
device_code_store = {}

class DeviceCodeResponse(BaseModel):
    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int

class DeviceTokenRequest(BaseModel):
    device_code: str

@router.post("/github/device-code", response_model=DeviceCodeResponse)
async def initiate_github_device_flow():
    """Initiate GitHub Device Code flow for Node 08 Bridge authentication"""
    if not settings.ENABLE_GITHUB_AUTH or not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub authentication not enabled"
        )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://github.com/login/device/code",
                data={"client_id": settings.GITHUB_CLIENT_ID},
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            
            # Store device code for polling
            device_code_store[data["device_code"]] = {
                "created_at": timedelta(seconds=0),
                "user_code": data["user_code"]
            }
            
            return DeviceCodeResponse(**data)
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"GitHub API error: {str(e)}"
            )

@router.post("/github/poll-token")
async def poll_github_token(request: DeviceTokenRequest):
    """Poll for GitHub access token after user authorization"""
    if not settings.ENABLE_GITHUB_AUTH or not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub authentication not enabled"
        )
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "device_code": request.device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
                },
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                return {"status": "pending", "error": data["error"]}
            
            # Create our internal JWT token
            access_token = create_access_token(
                data={"sub": "github_user", "github_token": data.get("access_token")},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            return {
                "status": "complete",
                "access_token": access_token,
                "token_type": "bearer"
            }
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"GitHub API error: {str(e)}"
            )
