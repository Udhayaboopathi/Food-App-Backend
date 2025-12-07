"""
Authentication schemas for JWT and user auth
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token data"""
    email: Optional[str] = None
    user_id: Optional[str] = None


class UserLogin(BaseModel):
    """User login credentials"""
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """User registration data"""
    name: str
    email: EmailStr
    phone: str
    password: str
    address: Optional[str] = None


class UserResponse(BaseModel):
    """User data response"""
    id: str
    name: str
    email: str
    phone: str
    address: Optional[str]
    profile_image: Optional[str] = None
    role: str
    restaurant_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True
