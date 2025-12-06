"""
Order schemas for order management
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class OrderItemCreate(BaseModel):
    """Schema for creating an order item"""
    menu_item_id: int
    quantity: int


class OrderItemResponse(BaseModel):
    """Order item response"""
    id: int
    menu_item_id: int
    quantity: int
    price_at_purchase: float
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Schema for creating an order"""
    restaurant_id: int
    delivery_address: str
    payment_method: str = "cash"
    items: List[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    status: str


class OrderResponse(BaseModel):
    """Order response with all fields"""
    id: int
    user_id: int
    restaurant_id: int
    delivery_agent_id: Optional[int]
    total_amount: float
    delivery_address: str
    status: str
    payment_method: str
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True
