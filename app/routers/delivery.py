"""
Delivery agent router for delivery management
Handles delivery agent operations and order assignments
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from ..core.database import get_session
from ..core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from ..models import DeliveryAgent, Order, User
from ..schemas.auth import Token
from .auth import get_current_user
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/delivery", tags=["Delivery Agents"])


class DeliveryAgentRegister(BaseModel):
    """Delivery agent registration schema"""
    name: str
    email: EmailStr
    phone: str
    password: str
    vehicle_type: str
    vehicle_number: str


class DeliveryAgentLogin(BaseModel):
    """Delivery agent login schema"""
    email: EmailStr
    password: str


class DeliveryAgentResponse(BaseModel):
    """Delivery agent response schema"""
    id: int
    name: str
    email: str
    phone: str
    vehicle_type: str
    vehicle_number: str
    is_active: bool
    is_available: bool
    
    class Config:
        from_attributes = True


@router.post("/register", response_model=DeliveryAgentResponse, status_code=status.HTTP_201_CREATED)
def register_delivery_agent(
    agent_data: DeliveryAgentRegister,
    session: Session = Depends(get_session)
):
    """
    Register a new delivery agent
    
    Args:
        agent_data: Delivery agent registration information
        session: Database session
    
    Returns:
        Created delivery agent data
    """
    # Check if email already exists
    statement = select(DeliveryAgent).where(DeliveryAgent.email == agent_data.email)
    existing_agent = session.exec(statement).first()
    
    if existing_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new delivery agent
    hashed_password = get_password_hash(agent_data.password)
    new_agent = DeliveryAgent(
        name=agent_data.name,
        email=agent_data.email,
        phone=agent_data.phone,
        hashed_password=hashed_password,
        vehicle_type=agent_data.vehicle_type,
        vehicle_number=agent_data.vehicle_number
    )
    
    session.add(new_agent)
    session.commit()
    session.refresh(new_agent)
    
    return new_agent


@router.post("/login", response_model=Token)
def login_delivery_agent(
    login_data: DeliveryAgentLogin,
    session: Session = Depends(get_session)
):
    """
    Login as delivery agent
    
    Args:
        login_data: Login credentials
        session: Database session
    
    Returns:
        JWT tokens
    """
    statement = select(DeliveryAgent).where(DeliveryAgent.email == login_data.email)
    agent = session.exec(statement).first()
    
    if not agent or not verify_password(login_data.password, agent.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent account is inactive"
        )
    
    # Create tokens with delivery role
    access_token = create_access_token(data={"sub": agent.email, "agent_id": agent.id, "role": "delivery"})
    refresh_token = create_refresh_token(data={"sub": agent.email, "agent_id": agent.id, "role": "delivery"})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/orders/pending", response_model=List)
def get_pending_orders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get pending orders available for pickup (Delivery agents only)
    
    Args:
        session: Database session
        current_user: Current authenticated delivery agent
    
    Returns:
        List of pending orders
    """
    if current_user.role != "delivery":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only delivery agents can access this endpoint"
        )
    
    statement = select(Order).where(
        Order.status == "preparing",
        Order.delivery_agent_id == None
    )
    orders = session.exec(statement).all()
    return orders


@router.post("/orders/{order_id}/accept")
def accept_order(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Accept an order for delivery
    
    Args:
        order_id: Order ID
        session: Database session
        current_user: Current authenticated delivery agent
    
    Returns:
        Success message
    """
    if current_user.role != "delivery":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only delivery agents can accept orders"
        )
    
    order = session.get(Order, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.delivery_agent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already assigned to another agent"
        )
    
    # Get agent ID from user (assuming delivery user has agent_id)
    # This is a simplified approach - in production, you'd have a proper agent lookup
    statement = select(DeliveryAgent).where(DeliveryAgent.email == current_user.email)
    agent = session.exec(statement).first()
    
    if agent:
        order.delivery_agent_id = agent.id
        order.status = "out_for_delivery"
        session.add(order)
        session.commit()
    
    return {"message": "Order accepted successfully"}


@router.get("/agents", response_model=List[DeliveryAgentResponse])
def get_all_agents(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all delivery agents (Admin only)
    
    Args:
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        List of delivery agents
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all agents"
        )
    
    statement = select(DeliveryAgent)
    agents = session.exec(statement).all()
    return agents
