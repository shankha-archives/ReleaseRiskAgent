"""
FastAPI Main Entrypoint
Risk Level: LOW - Simple entrypoint with minimal logic
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.login import router as auth_router
from app.auth.oauth import router as oauth_router
from app.payment.processor import router as payment_router
from app.users.crud import router as users_router
from app.utils.helpers import get_app_info

app = FastAPI(
    title="Dummy App",
    description="A test application for R3 Agent E2E testing",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(oauth_router, prefix="/api/oauth", tags=["oauth"])
app.include_router(payment_router, prefix="/api/payment", tags=["payment"])
app.include_router(users_router, prefix="/api/users", tags=["users"])


@app.get("/")
async def root():
    """Root endpoint - returns app info."""
    return get_app_info()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
