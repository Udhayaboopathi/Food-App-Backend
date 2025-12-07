"""
Menu item schemas for CRUD operations
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MenuItemBase(BaseModel):
    """Base menu item schema"""
    name: str
    description: Optional[str] = None
    price: float
    category: str
    image: Optional[str] = None
    is_veg: bool = True


class MenuItemCreate(MenuItemBase):
    """Schema for creating a menu item"""
    restaurant_id: str


class MenuItemCreateForOwner(MenuItemBase):
    """Schema for owner creating a menu item (restaurant_id auto-assigned)"""
    pass


class MenuItemUpdate(BaseModel):
    """Schema for updating a menu item"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image: Optional[str] = None
    is_veg: Optional[bool] = None
    is_available: Optional[bool] = None


class MenuItemResponse(MenuItemBase):
    """Menu item response with all fields"""
    id: str
    restaurant_id: str
    is_available: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True
