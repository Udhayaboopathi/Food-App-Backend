"""
Review model for restaurant ratings and feedback
Allows users to rate and comment on restaurants
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class Review(SQLModel, table=True):
    """Restaurant review model"""
    
    __tablename__ = "reviews"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    restaurant_id: int = Field(foreign_key="restaurants.id", index=True)
    rating: int = Field(ge=1, le=5)  # 1 to 5 stars
    comment: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="reviews")
    restaurant: Optional["Restaurant"] = Relationship(back_populates="reviews")
