"""
MenuItem model for food items
Stores menu items with pricing and categories
"""
from typing import Optional
from beanie import Document
from pydantic import Field
from datetime import datetime


class MenuItem(Document):
    """Menu item model"""
    
    restaurant_id: str  # MongoDB ObjectId as string
    name: str
    description: Optional[str] = None
    price: float = Field(ge=0)
    category: str  # Appetizer, Main Course, Dessert, Beverage
    image: Optional[str] = None  # Image URL
    is_veg: bool = True
    is_available: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "menu_items"
        indexes = ["restaurant_id"]
