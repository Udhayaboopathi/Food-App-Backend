"""
Review schemas for restaurant reviews
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    """Schema for creating a review"""
    restaurant_id: int
    rating: int  # 1 to 5
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    """Review response with all fields"""
    id: int
    user_id: int
    restaurant_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
