"""
Review model for restaurant ratings and feedback
Allows users to rate and comment on restaurants
"""
from typing import Optional
from beanie import Document
from pydantic import Field
from datetime import datetime


class Review(Document):
    """Restaurant review model"""
    
    user_id: str  # MongoDB ObjectId as string
    restaurant_id: str  # MongoDB ObjectId as string
    rating: int = Field(ge=1, le=5)  # 1 to 5 stars
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "reviews"
        indexes = ["user_id", "restaurant_id"]
