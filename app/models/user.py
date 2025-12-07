"""
User model for customer accounts
Handles authentication and user profile data
"""
from typing import Optional
from beanie import Document
from pydantic import Field, EmailStr
from datetime import datetime


class User(Document):
    """User account model"""
    
    name: str
    email: EmailStr = Field(unique=True)
    phone: str
    hashed_password: str
    address: Optional[str] = None
    profile_image: Optional[str] = None  # URL to profile image
    role: str = "user"  # user, admin, delivery, owner
    is_active: bool = True
    restaurant_id: Optional[str] = None  # MongoDB ObjectId as string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = ["email"]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "1234567890"
            }
        }
