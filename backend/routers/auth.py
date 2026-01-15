from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.core.security import (
    verify_admin_credentials,
    create_access_token,
    get_current_admin,
)

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(req: LoginRequest):
    if not verify_admin_credentials(req.username, req.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(req.username)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def me(admin: str = Depends(get_current_admin)):
    return {"username": admin, "role": "admin"}
