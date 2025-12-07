"""
Order models for order management
Handles order tracking and order items
"""
from typing import Optional, List
from beanie import Document
from pydantic import Field, BaseModel
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItemData(BaseModel):
    """Individual item in an order (embedded document)"""
    menu_item_id: str
    quantity: int = Field(ge=1)
    price_at_purchase: float = Field(ge=0)


class Order(Document):
    """Order model"""
    
    user_id: str  # MongoDB ObjectId as string
    restaurant_id: str  # MongoDB ObjectId as string
    delivery_agent_id: Optional[str] = None  # MongoDB ObjectId as string
    total_amount: float = Field(ge=0)
    delivery_address: str
    status: str = OrderStatus.PENDING
    payment_method: str = "cash"  # cash, card, upi
    items: List[OrderItemData] = []  # Embedded order items
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "orders"
        indexes = ["user_id", "restaurant_id"]


class OrderItem(Document):
    """Individual items in an order (separate collection for compatibility)"""
    
    order_id: str  # MongoDB ObjectId as string
    menu_item_id: str  # MongoDB ObjectId as string
    quantity: int = Field(ge=1)
    price_at_purchase: float = Field(ge=0)
    
    class Settings:
        name = "order_items"
        indexes = ["order_id"]
