"""
MenuItem model for food items
Stores menu items with pricing and categories
"""
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class MenuItem(SQLModel, table=True):
    """Menu item model"""
    
    __tablename__ = "menu_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant_id: int = Field(foreign_key="restaurants.id", index=True)
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(ge=0)
    category: str = Field(max_length=50)  # Appetizer, Main Course, Dessert, Beverage
    image: Optional[str] = Field(default=None, max_length=500)  # Image URL
    is_veg: bool = Field(default=True)
    is_available: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    restaurant: Optional["Restaurant"] = Relationship(back_populates="menu_items")
    order_items: List["OrderItem"] = Relationship(back_populates="menu_item")
