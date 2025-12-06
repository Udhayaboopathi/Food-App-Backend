"""
DeliveryAgent model for delivery personnel
Manages delivery agent information and availability
"""
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class DeliveryAgent(SQLModel, table=True):
    """Delivery agent model"""
    
    __tablename__ = "delivery_agents"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    phone: str = Field(max_length=15, unique=True)
    email: str = Field(unique=True, max_length=255)
    hashed_password: str
    vehicle_type: str = Field(max_length=50)  # Bike, Scooter, Car
    vehicle_number: str = Field(max_length=20)
    is_active: bool = Field(default=True)
    is_available: bool = Field(default=True)  # Currently available for orders
    location: Optional[str] = Field(default=None, max_length=200)  # Current location
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    orders: List["Order"] = Relationship(back_populates="delivery_agent")
