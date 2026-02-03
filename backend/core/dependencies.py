"""
FastAPI Dependencies
Provides reusable dependency injection for routes.

Note: This module provides a simplified get_current_user dependency for use in routers.
For more complex authentication logic, see backend.core.security module.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.core.security import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Simplified dependency to get the current authenticated user from JWT token.
    
    This is a convenience wrapper around verify_token() for use in router dependencies.
    For the full authentication flow, see backend.core.security.get_current_user.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        dict: Token payload containing user information
        
    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
