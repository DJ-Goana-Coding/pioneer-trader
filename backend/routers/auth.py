from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.core.security import Token, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

# --- FRANKFURT RESCUE DATABASE ---
# This replaces the old fake_users_db variable entirely
users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Commander",
        "email": "admin@frankfurt.base",
        "hashed_password": "$pbkdf2-sha256$12000$mZNSai0FQKg1RkgJwXhvLQ$JkfBGq6hdH52YITLS9EB8oxZ5av70kAQ/hrWMnRUWiY"
    }
}

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    # Pass the users_db explicitly to authenticate_user if possible, 
    # or rely on the security module to look it up if it's integrated there.
    # Since we are fixing auth.py, we handle the lookup here or rely on the standard pattern.
    
    # Standard Pattern for this bot:
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}