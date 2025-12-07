"""
Orders router for order management (MongoDB version)
Handles order creation, tracking, and status updates
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from beanie import PydanticObjectId

from ..models.order import Order, OrderItemData
from ..models.menu_item import MenuItem
from ..models.user import User
from ..schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from .auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order
    
    Args:
        order_data: Order information with items
        current_user: Current authenticated user
    
    Returns:
        Created order data
    """
    # Calculate total amount
    total_amount = 0.0
    order_items_list = []
    
    for item in order_data.items:
        try:
            menu_item = await MenuItem.get(PydanticObjectId(item.menu_item_id))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item {item.menu_item_id} not found"
            )
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item {item.menu_item_id} not found"
            )
        
        if not menu_item.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu item {menu_item.name} is not available"
            )
        
        item_total = menu_item.price * item.quantity
        total_amount += item_total
        
        order_items_list.append(
            OrderItemData(
                menu_item_id=str(menu_item.id),
                quantity=item.quantity,
                price_at_purchase=menu_item.price
            )
        )
    
    # Create order
    new_order = Order(
        user_id=str(current_user.id),
        restaurant_id=order_data.restaurant_id,
        delivery_address=order_data.delivery_address,
        payment_method=order_data.payment_method,
        total_amount=total_amount,
        items=order_items_list,
        status="pending"
    )
    
    await new_order.insert()
    
    # Convert to dict with proper ID serialization
    order_dict = new_order.model_dump(by_alias=False)
    order_dict["id"] = str(new_order.id)
    
    return order_dict


@router.get("")
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    status: str = None
):
    """
    Get all orders for the current user
    
    Args:
        current_user: Current authenticated user
        status: Filter by order status
    
    Returns:
        List of orders
    """
    query = {"user_id": str(current_user.id)}
    
    if status:
        query["status"] = status
    
    orders = await Order.find(query).sort(-Order.created_at).to_list()
    
    # Convert to dict with proper ID serialization
    result = []
    for order in orders:
        order_dict = order.model_dump(by_alias=False)
        order_dict["id"] = str(order.id)
        result.append(order_dict)
    
    return result


@router.get("/user/{user_id}")
async def get_orders_by_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    status: str = None
):
    """
    Get all orders for a specific user (Admin only)
    
    Args:
        user_id: User ID to get orders for
        current_user: Current authenticated user
        status: Filter by order status
    
    Returns:
        List of orders for the user
    """
    # Only admins can view other users' orders
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view other users' orders"
        )
    
    query = {"user_id": user_id}
    
    if status:
        query["status"] = status
    
    orders = await Order.find(query).sort(-Order.created_at).to_list()
    
    # Convert to dict with proper ID serialization
    result = []
    for order in orders:
        order_dict = order.model_dump(by_alias=False)
        order_dict["id"] = str(order.id)
        result.append(order_dict)
    
    return result


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a single order by ID
    
    Args:
        order_id: Order ID
        current_user: Current authenticated user
    
    Returns:
        Order data
    """
    try:
        order = await Order.get(PydanticObjectId(order_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check authorization
    if order.user_id != str(current_user.id) and current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    # Convert to dict with proper ID serialization
    order_dict = order.model_dump(by_alias=False)
    order_dict["id"] = str(order.id)
    if order.user_id:
        order_dict["user_id"] = str(order.user_id)
    if order.restaurant_id:
        order_dict["restaurant_id"] = str(order.restaurant_id)
    
    return order_dict


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update order status (Admin/Owner only)
    
    Args:
        order_id: Order ID to update
        status_update: New status
        current_user: Current authenticated user
    
    Returns:
        Updated order data
    """
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and restaurant owners can update order status"
        )
    
    try:
        order = await Order.get(PydanticObjectId(order_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.status = status_update.status
    order.updated_at = datetime.utcnow()
    
    await order.save()
    
    # Convert to dict with proper ID serialization
    order_dict = order.model_dump(by_alias=False)
    order_dict["id"] = str(order.id)
    if order.user_id:
        order_dict["user_id"] = str(order.user_id)
    if order.restaurant_id:
        order_dict["restaurant_id"] = str(order.restaurant_id)
    
    return order_dict


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an order (Only if pending)
    
    Args:
        order_id: Order ID to cancel
        current_user: Current authenticated user
    """
    try:
        order = await Order.get(PydanticObjectId(order_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check authorization
    if order.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this order"
        )
    
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only cancel pending orders"
        )
    
    order.status = "cancelled"
    order.updated_at = datetime.utcnow()
    await order.save()
