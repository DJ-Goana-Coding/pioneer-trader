from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
# We import Token/create_access_token so the system generates a valid session
from backend.core.security import Token, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

# 1. SIMPLE USER DB
users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Commander",
        "email": "admin@frankfurt.base",
        # We don't even need the hash anymore for the backdoor
        "hashed_password": "ignored_placeholder"
    }
}

# 2. THE BACKDOOR AUTHENTICATION LOGIC
def authenticate_user(users_db, username, password):
    user = users_db.get(username)
    if not user:
        return False
        
    # --- THE BACKDOOR ---
    # We explicitly check for your specific password string.
    # No hashing. No encryption libraries. Just a string check.
    if password == "Tia-sue1104!!":
        return user
    # --------------------

    return False

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        # If it fails, we print WHY to the logs (for debugging)
        print(f"❌ LOGIN FAILED. User: {form_data.username}, Pass provided: {form_data.password}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # If successful, create the session token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}