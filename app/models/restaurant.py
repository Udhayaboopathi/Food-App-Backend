"""
Restaurant model for food outlets
Stores restaurant information and metadata
"""
from typing import Optional
from beanie import Document
from pydantic import Field
from datetime import datetime


class Restaurant(Document):
    """Restaurant information model"""
    
    name: str
    city: str
    address: str
    cuisine: str  # Italian, Chinese, Indian, etc.
    rating: float = Field(default=0.0, ge=0, le=5)
    thumbnail: Optional[str] = None  # Image URL
    delivery_time: int = 30  # Minutes
    is_active: bool = True
    owner_id: Optional[str] = None  # MongoDB ObjectId as string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "restaurants"
