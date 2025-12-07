"""
Order schemas for order management
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class OrderItemCreate(BaseModel):
    """Schema for creating an order item"""
    menu_item_id: str
    quantity: int


class OrderItemResponse(BaseModel):
    """Order item response"""
    id: str
    menu_item_id: str
    quantity: int
    price_at_purchase: float
    
    class Config:
        from_attributes = True
        populate_by_name = True


class OrderCreate(BaseModel):
    """Schema for creating an order"""
    restaurant_id: str
    delivery_address: str
    payment_method: str = "cash"
    items: List[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    status: str


class OrderResponse(BaseModel):
    """Order response with all fields"""
    id: str
    user_id: str
    restaurant_id: str
    delivery_agent_id: Optional[str]
    total_amount: float
    delivery_address: str
    status: str
    payment_method: str
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True
        populate_by_name = True
