"""
OAuth Implementation Module
Risk Level: HIGH - OAuth flows are security-critical

Contains intentional issues:
- Hardcoded client secrets
- Missing state validation
- Insecure token handling
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import hashlib
import time
import json
import base64

router = APIRouter()

# INTENTIONAL VULNERABILITY: Hardcoded OAuth credentials
GOOGLE_CLIENT_ID = "123456789-abcdefghij.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "GOCSPX-abcdefghijklmnop"
GITHUB_CLIENT_ID = "Iv1.abc123def456"
GITHUB_CLIENT_SECRET = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# OAuth state storage (in-memory, insecure for demo)
oauth_states = {}


class OAuthConfig(BaseModel):
    provider: str
    client_id: str
    redirect_uri: str
    scope: str


class OAuthCallback(BaseModel):
    code: str
    state: Optional[str] = None


class OAuthToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None


def generate_state() -> str:
    """Generate OAuth state parameter."""
    return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]


def encode_token(data: dict) -> str:
    """
    Encode token data.
    INTENTIONAL: Using base64 instead of proper encryption
    """
    json_data = json.dumps(data)
    return base64.b64encode(json_data.encode()).decode()


def decode_token(token: str) -> dict:
    """
    Decode token data.
    INTENTIONAL: No signature verification
    """
    try:
        json_data = base64.b64decode(token.encode()).decode()
        return json.loads(json_data)
    except:
        # INTENTIONAL: Bare except
        return {}


@router.get("/google/authorize")
async def google_authorize(redirect_uri: str):
    """
    Initiate Google OAuth flow.
    """
    state = generate_state()
    # INTENTIONAL: State stored in memory without expiration
    oauth_states[state] = {"provider": "google", "redirect_uri": redirect_uri}
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=email profile"
        f"&state={state}"
    )
    return {"auth_url": auth_url, "state": state}


@router.get("/google/callback")
async def google_callback(code: str, state: Optional[str] = None):
    """
    Handle Google OAuth callback.
    INTENTIONAL ISSUES:
    - State validation is optional
    - No PKCE verification
    """
    try:
        # INTENTIONAL: State validation is weak
        if state and state not in oauth_states:
            # Just log warning but continue anyway
            print(f"Warning: Unknown state {state}")
        
        # INTENTIONAL: Simulate token exchange without actual API call
        fake_token = encode_token({
            "provider": "google",
            "user_id": "google_user_123",
            "email": "user@example.com",
            "issued_at": int(time.time())
        })
        
        return OAuthToken(
            access_token=fake_token,
            token_type="bearer",
            expires_in=3600,
            refresh_token=encode_token({"refresh": True})
        )
    except Exception as e:
        # INTENTIONAL: Exposing error details
        raise HTTPException(status_code=400, detail=f"OAuth failed: {str(e)}")


@router.get("/github/authorize")
async def github_authorize(redirect_uri: str):
    """Initiate GitHub OAuth flow."""
    state = generate_state()
    oauth_states[state] = {"provider": "github", "redirect_uri": redirect_uri}
    
    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=user:email"
        f"&state={state}"
    )
    return {"auth_url": auth_url, "state": state}


@router.get("/github/callback")
async def github_callback(code: str, state: Optional[str] = None):
    """
    Handle GitHub OAuth callback.
    INTENTIONAL: Similar issues as Google callback
    """
    try:
        # Weak state validation
        if state:
            if state not in oauth_states:
                pass  # INTENTIONAL: Ignore invalid state
        
        fake_token = encode_token({
            "provider": "github",
            "user_id": "github_user_456",
            "username": "testuser",
            "issued_at": int(time.time())
        })
        
        return OAuthToken(
            access_token=fake_token,
            token_type="bearer",
            expires_in=3600
        )
    except:
        # INTENTIONAL: Bare except with generic error
        raise HTTPException(status_code=500, detail="OAuth error")


@router.post("/token/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token.
    INTENTIONAL: No token rotation
    """
    try:
        data = decode_token(refresh_token)
        if not data:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # INTENTIONAL: Reusing same refresh token
        new_access_token = encode_token({
            "refreshed": True,
            "issued_at": int(time.time())
        })
        
        return OAuthToken(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=3600,
            refresh_token=refresh_token  # INTENTIONAL: Same refresh token
        )
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=500, detail="Token refresh failed")


@router.delete("/token/revoke")
async def revoke_token(token: str):
    """
    Revoke access token.
    INTENTIONAL: Token not actually revoked
    """
    # TODO: Implement actual token revocation
    return {"message": "Token revoked", "revoked": True}
