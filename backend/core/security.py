from passlib.context import CryptContext
import os

# FRANKFURT HARD-WIRE: FORCE PBKDF2 TO BYPASS BCRYPT 72-BYTE LIMIT
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"], 
    deprecated="auto",
    pbkdf2_sha256__rounds=12000
)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    # PBKDF2 handles long passwords safely
    return pwd_context.hash(password)