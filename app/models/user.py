"""
User model for customer accounts
Handles authentication and user profile data
"""
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class User(SQLModel, table=True):
    """User account model"""
    
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True, max_length=255)
    phone: str = Field(max_length=15)
    hashed_password: str
    address: Optional[str] = Field(default=None, max_length=500)
    role: str = Field(default="user", max_length=20)  # user, admin, delivery, owner
    is_active: bool = Field(default=True)
    restaurant_id: Optional[int] = Field(default=None, foreign_key="restaurants.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    orders: List["Order"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")
