from datetime import datetime, timedelta
from typing import Optional, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
import os

# --- CONFIGURATION ---
# We use defaults if env vars are missing to prevent crashes
SECRET_KEY = os.getenv("SECRET_KEY", "frankfurt_secret_key_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- THE MISSING MODELS (This fixes the ImportError) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

# --- THE HARD-WIRED ENGINE (Fixes the 72-byte bug) ---
# We force PBKDF2 to bypass the Bcrypt limitation
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"], 
    deprecated="auto",
    pbkdf2_sha256__rounds=12000
)

# --- UTILITY FUNCTIONS ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user():
    # Placeholder if needed by other modules, but auth.py handles the main logic now
    pass