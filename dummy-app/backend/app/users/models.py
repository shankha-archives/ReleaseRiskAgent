"""
User Models Module
Risk Level: MEDIUM - Data model definitions

Contains:
- User data models
- Role definitions
- Permission structures
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class Permission(str, Enum):
    """Permission types."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    full_name: Optional[str] = None


class UserCreateModel(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.USER


class UserUpdateModel(BaseModel):
    """User update model."""
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserInDB(UserBase):
    """User model as stored in database."""
    id: str
    password_hash: str
    role: UserRole
    status: UserStatus
    permissions: List[Permission]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None


class UserPublic(UserBase):
    """Public user model (excludes sensitive data)."""
    id: str
    role: UserRole
    status: UserStatus
    created_at: datetime


class UserProfile(BaseModel):
    """Extended user profile."""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime


class UserSession(BaseModel):
    """User session model."""
    session_id: str
    user_id: str
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    is_active: bool = True


class RolePermissions(BaseModel):
    """Role to permissions mapping."""
    role: UserRole
    permissions: List[Permission]

    @classmethod
    def get_default_permissions(cls, role: UserRole) -> List[Permission]:
        """Get default permissions for a role."""
        permission_map = {
            UserRole.ADMIN: [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN],
            UserRole.MODERATOR: [Permission.READ, Permission.WRITE, Permission.DELETE],
            UserRole.USER: [Permission.READ, Permission.WRITE],
            UserRole.GUEST: [Permission.READ]
        }
        return permission_map.get(role, [Permission.READ])


# TODO: Add user preferences model
# TODO: Add notification settings model
# TODO: Add API key model for user authentication
