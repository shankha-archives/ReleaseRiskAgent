"""
User CRUD Operations Module
Risk Level: MEDIUM - User data management

Contains intentional issues:
- Some test coverage gaps
- TODO comments
- Moderate complexity
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import hashlib
import time
import re

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: int


# In-memory user storage
users_db = {}


def generate_user_id() -> str:
    """Generate unique user ID."""
    return f"user_{hashlib.md5(str(time.time()).encode()).hexdigest()[:12]}"


def hash_password(password: str) -> str:
    """
    Hash password for storage.
    TODO: Use bcrypt instead of SHA-256
    """
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """
    Validate username format.
    TODO: Add more validation rules
    """
    if len(username) < 3 or len(username) > 50:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    """
    Create a new user.
    """
    # Validate input
    if not validate_username(user.username):
        raise HTTPException(status_code=400, detail="Invalid username format")
    
    if not validate_email(user.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Check for existing user
    for existing_user in users_db.values():
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=409, detail="Username already exists")
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=409, detail="Email already exists")
    
    # Create user
    user_id = generate_user_id()
    new_user = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "full_name": user.full_name,
        "is_active": True,
        "created_at": int(time.time()),
        "updated_at": int(time.time())
    }
    users_db[user_id] = new_user
    
    return UserResponse(
        id=user_id,
        username=new_user["username"],
        email=new_user["email"],
        full_name=new_user["full_name"],
        is_active=new_user["is_active"],
        created_at=new_user["created_at"]
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        is_active=user["is_active"],
        created_at=user["created_at"]
    )


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = None
):
    """
    List users with pagination.
    TODO: Add sorting options
    """
    users = list(users_db.values())
    
    # Filter by active status
    if is_active is not None:
        users = [u for u in users if u["is_active"] == is_active]
    
    # Apply pagination
    paginated = users[skip:skip + limit]
    
    return [
        UserResponse(
            id=u["id"],
            username=u["username"],
            email=u["email"],
            full_name=u["full_name"],
            is_active=u["is_active"],
            created_at=u["created_at"]
        )
        for u in paginated
    ]


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate):
    """
    Update user details.
    """
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    
    # Update fields
    if user_update.email is not None:
        if not validate_email(user_update.email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        # TODO: Check for duplicate email
        user["email"] = user_update.email
    
    if user_update.full_name is not None:
        user["full_name"] = user_update.full_name
    
    if user_update.is_active is not None:
        user["is_active"] = user_update.is_active
    
    user["updated_at"] = int(time.time())
    users_db[user_id] = user
    
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        is_active=user["is_active"],
        created_at=user["created_at"]
    )


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """
    Delete a user.
    TODO: Implement soft delete instead
    """
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    del users_db[user_id]
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/deactivate")
async def deactivate_user(user_id: str):
    """Deactivate a user account."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    users_db[user_id]["is_active"] = False
    users_db[user_id]["updated_at"] = int(time.time())
    
    return {"message": "User deactivated"}


@router.post("/{user_id}/activate")
async def activate_user(user_id: str):
    """Activate a user account."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    users_db[user_id]["is_active"] = True
    users_db[user_id]["updated_at"] = int(time.time())
    
    return {"message": "User activated"}


def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username."""
    for user in users_db.values():
        if user["username"] == username:
            return user
    return None


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email."""
    for user in users_db.values():
        if user["email"] == email:
            return user
    return None
