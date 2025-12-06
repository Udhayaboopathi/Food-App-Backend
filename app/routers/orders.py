"""
Orders router for order management
Handles order creation, tracking, and status updates
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from ..core.database import get_session
from ..models import Order, OrderItem, MenuItem, User
from ..schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from .auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order
    
    Args:
        order_data: Order information with items
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        Created order data
    """
    # Calculate total amount
    total_amount = 0.0
    order_items_data = []
    
    for item in order_data.items:
        menu_item = session.get(MenuItem, item.menu_item_id)
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item {item.menu_item_id} not found"
            )
        
        if not menu_item.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu item '{menu_item.name}' is not available"
            )
        
        item_total = menu_item.price * item.quantity
        total_amount += item_total
        
        order_items_data.append({
            "menu_item_id": item.menu_item_id,
            "quantity": item.quantity,
            "price_at_purchase": menu_item.price
        })
    
    # Create order
    new_order = Order(
        user_id=current_user.id,
        restaurant_id=order_data.restaurant_id,
        total_amount=total_amount,
        delivery_address=order_data.delivery_address,
        payment_method=order_data.payment_method,
        status="pending"
    )
    
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    
    # Create order items
    for item_data in order_items_data:
        order_item = OrderItem(order_id=new_order.id, **item_data)
        session.add(order_item)
    
    session.commit()
    session.refresh(new_order)
    
    return new_order


@router.get("", response_model=List[OrderResponse])
def get_user_orders(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all orders for current user
    
    Args:
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        List of user's orders
    """
    statement = select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc())
    orders = session.exec(statement).all()
    return orders


@router.get("/user/{user_id}", response_model=List[OrderResponse])
def get_orders_by_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all orders for a specific user (Admin only)
    
    Args:
        user_id: User ID to get orders for
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        List of user's orders
    """
    # Only admin can access other users' orders
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access other users' orders"
        )
    
    statement = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    orders = session.exec(statement).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get single order by ID
    
    Args:
        order_id: Order ID
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        Order data
    """
    order = session.get(Order, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Users can only view their own orders, admins can view all
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update order status (Admin or Delivery Agent only)
    
    Args:
        order_id: Order ID
        status_data: New status
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated order data
    """
    # Check permissions
    if current_user.role not in ["admin", "delivery"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and delivery agents can update order status"
        )
    
    order = session.get(Order, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update status
    order.status = status_data.status
    order.updated_at = datetime.utcnow()
    
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return order


@router.get("/all/admin", response_model=List[OrderResponse])
def get_all_orders_admin(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all orders (Admin only)
    
    Args:
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        List of all orders
    """
    # Check admin role
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all orders"
        )
    
    statement = select(Order).order_by(Order.created_at.desc())
    orders = session.exec(statement).all()
    return orders
