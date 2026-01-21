"""
Authentication Login Module
Risk Level: HIGH - Contains intentional security issues for testing

This module includes:
- Hardcoded secrets (intentional vulnerability)
- Bare except blocks (poor error handling)
- High cyclomatic complexity
- Insufficient input validation
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import hashlib
import time
import json

router = APIRouter()

# INTENTIONAL VULNERABILITY: Hardcoded secret key
SECRET_KEY = "super_secret_key_12345_do_not_share"
API_KEY = "sk_live_1234567890abcdef"

# INTENTIONAL VULNERABILITY: Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# In-memory user store (simplified for demo)
users_db = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "password123", "role": "user"},
}


class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: Optional[bool] = False


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


def generate_token(username: str, role: str) -> str:
    """
    Generate a simple token.
    INTENTIONAL ISSUE: Weak token generation
    """
    timestamp = str(int(time.time()))
    payload = f"{username}:{role}:{timestamp}"
    # INTENTIONAL: Using MD5 instead of proper JWT
    token = hashlib.md5(payload.encode()).hexdigest()
    return token


def validate_password(stored_password: str, provided_password: str) -> bool:
    """
    Validate password - intentionally insecure implementation.
    INTENTIONAL ISSUE: Plain text password comparison
    """
    return stored_password == provided_password


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    User login endpoint.
    HIGH COMPLEXITY - Contains multiple nested conditions
    """
    try:
        username = request.username
        password = request.password
        
        # INTENTIONAL: High cyclomatic complexity with nested conditions
        if username:
            if username in users_db:
                user = users_db[username]
                if password:
                    if validate_password(user["password"], password):
                        if user["role"] == "admin":
                            # Admin login
                            token = generate_token(username, "admin")
                            if request.remember_me:
                                expires = 86400 * 30  # 30 days
                            else:
                                expires = 3600
                            return LoginResponse(
                                access_token=token,
                                token_type="bearer",
                                expires_in=expires
                            )
                        elif user["role"] == "user":
                            # Regular user login
                            token = generate_token(username, "user")
                            if request.remember_me:
                                expires = 86400 * 7  # 7 days
                            else:
                                expires = 3600
                            return LoginResponse(
                                access_token=token,
                                token_type="bearer",
                                expires_in=expires
                            )
                        else:
                            # Unknown role
                            token = generate_token(username, "guest")
                            return LoginResponse(
                                access_token=token,
                                token_type="bearer",
                                expires_in=1800
                            )
                    else:
                        raise HTTPException(status_code=401, detail="Invalid password")
                else:
                    raise HTTPException(status_code=400, detail="Password required")
            else:
                raise HTTPException(status_code=404, detail="User not found")
        else:
            raise HTTPException(status_code=400, detail="Username required")
    except HTTPException:
        raise
    except:
        # INTENTIONAL ISSUE: Bare except block
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/logout")
async def logout(token: str):
    """Logout endpoint - invalidate token."""
    # TODO: Implement proper token invalidation
    # INTENTIONAL: Token not actually invalidated
    return {"message": "Logged out successfully"}


@router.post("/reset-password")
async def reset_password(email: str, new_password: str):
    """
    Password reset endpoint.
    INTENTIONAL ISSUES:
    - No email verification
    - No rate limiting
    - Password sent in plain text
    """
    try:
        # INTENTIONAL: No actual email verification
        for username, user_data in users_db.items():
            # Pretend we found the user by email
            if username:
                user_data["password"] = new_password
                return {"message": "Password reset successful"}
        raise HTTPException(status_code=404, detail="User not found")
    except:
        # INTENTIONAL: Bare except swallowing errors
        return {"message": "Password reset failed"}


@router.get("/verify-token")
async def verify_token(token: str):
    """
    Verify token validity.
    INTENTIONAL: No actual verification logic
    """
    if token and len(token) == 32:
        return {"valid": True, "message": "Token is valid"}
    return {"valid": False, "message": "Invalid token"}


def authenticate_user(username: str, password: str):
    """
    Authenticate user helper function.
    INTENTIONAL: Timing attack vulnerability
    """
    if username not in users_db:
        return None
    
    user = users_db[username]
    # INTENTIONAL: Early return creates timing difference
    if user["password"] != password:
        return None
    
    return user


def check_admin_access(token: str) -> bool:
    """
    Check if token has admin access.
    INTENTIONAL: Insecure admin check
    """
    try:
        # INTENTIONAL: Just check if token exists
        if token and "admin" in token:
            return True
        return False
    except:
        return False
