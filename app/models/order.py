"""
Order models for order management
Handles order tracking and order items
"""
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
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


class Order(SQLModel, table=True):
    """Order model"""
    
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    restaurant_id: int = Field(foreign_key="restaurants.id", index=True)
    delivery_agent_id: Optional[int] = Field(default=None, foreign_key="delivery_agents.id")
    total_amount: float = Field(ge=0)
    delivery_address: str = Field(max_length=500)
    status: str = Field(default=OrderStatus.PENDING, max_length=50)
    payment_method: str = Field(default="cash", max_length=50)  # cash, card, upi
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="orders")
    restaurant: Optional["Restaurant"] = Relationship(back_populates="orders")
    delivery_agent: Optional["DeliveryAgent"] = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    """Individual items in an order"""
    
    __tablename__ = "order_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    menu_item_id: int = Field(foreign_key="menu_items.id")
    quantity: int = Field(ge=1)
    price_at_purchase: float = Field(ge=0)  # Store price at time of order
    
    # Relationships
    order: Optional["Order"] = Relationship(back_populates="order_items")
    menu_item: Optional["MenuItem"] = Relationship(back_populates="order_items")
