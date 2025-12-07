"""
DeliveryAgent model for delivery personnel
Manages delivery agent information and availability
"""
from typing import Optional
from beanie import Document
from pydantic import Field, EmailStr
from datetime import datetime


class DeliveryAgent(Document):
    """Delivery agent model"""
    
    name: str
    phone: str = Field(unique=True)
    email: EmailStr = Field(unique=True)
    hashed_password: str
    vehicle_type: str  # Bike, Scooter, Car
    vehicle_number: str
    is_active: bool = True
    is_available: bool = True  # Currently available for orders
    location: Optional[str] = None  # Current location
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "delivery_agents"
        indexes = ["phone", "email"]
