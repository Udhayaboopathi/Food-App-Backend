"""
Restaurant model for food outlets
Stores restaurant information and metadata
"""
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class Restaurant(SQLModel, table=True):
    """Restaurant information model"""
    
    __tablename__ = "restaurants"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    city: str = Field(max_length=100)
    address: str = Field(max_length=500)
    cuisine: str = Field(max_length=100)  # Italian, Chinese, Indian, etc.
    rating: float = Field(default=0.0, ge=0, le=5)
    thumbnail: Optional[str] = Field(default=None, max_length=500)  # Image URL
    delivery_time: int = Field(default=30)  # Minutes
    is_active: bool = Field(default=True)
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    menu_items: List["MenuItem"] = Relationship(back_populates="restaurant")
    orders: List["Order"] = Relationship(back_populates="restaurant")
    reviews: List["Review"] = Relationship(back_populates="restaurant")
