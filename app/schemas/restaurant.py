"""
Restaurant schemas for CRUD operations
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RestaurantBase(BaseModel):
    """Base restaurant schema"""
    name: str
    city: str
    address: str
    cuisine: str
    thumbnail: Optional[str] = None
    delivery_time: int = 30


class RestaurantCreate(RestaurantBase):
    """Schema for creating a restaurant"""
    pass


class RestaurantUpdate(BaseModel):
    """Schema for updating a restaurant"""
    name: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    cuisine: Optional[str] = None
    thumbnail: Optional[str] = None
    delivery_time: Optional[int] = None
    is_active: Optional[bool] = None


class RestaurantResponse(RestaurantBase):
    """Restaurant response with all fields"""
    id: int
    rating: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
