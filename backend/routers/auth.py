from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
# We only import the tools we KNOW exist in security.py
from backend.core.security import Token, create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

# 1. THE RESCUE DATABASE
users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Commander",
        "email": "admin@frankfurt.base",
        "hashed_password": "$pbkdf2-sha256$12000$mZNSai0FQKg1RkgJwXhvLQ$JkfBGq6hdH52YITLS9EB8oxZ5av70kAQ/hrWMnRUWiY"
    }
}

# 2. THE LOCAL LOGIC (No external dependencies risk)
def authenticate_user(users_db, username, password):
    user = users_db.get(username)
    if not user:
        return False
    # Use the verify_password from security.py which handles PBKDF2
    if not verify_password(password, user['hashed_password']):
        return False
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
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