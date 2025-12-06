"""
Owner Router
Restaurant owner dashboard endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from ..core.database import get_session
from ..routers.auth import get_current_user
from ..models.user import User
from ..models.restaurant import Restaurant
from ..models.menu_item import MenuItem
from ..models.order import Order, OrderStatus
from ..schemas.restaurant import RestaurantCreate, RestaurantUpdate
from ..schemas.menu_item import MenuItemCreateForOwner, MenuItemUpdate

router = APIRouter(prefix="/owner", tags=["Owner"])


def verify_owner(current_user: User) -> User:
    """Verify user is a restaurant owner"""
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Owner role required."
        )
    return current_user


@router.get("/restaurant")
def get_my_restaurant(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get owner's restaurant"""
    verify_owner(current_user)
    
    if not current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    restaurant = session.get(Restaurant, current_user.restaurant_id)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    return restaurant


@router.put("/restaurant")
def update_my_restaurant(
    restaurant_data: RestaurantUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update owner's restaurant"""
    verify_owner(current_user)
    
    if not current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    restaurant = session.get(Restaurant, current_user.restaurant_id)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    # Update fields
    update_data = restaurant_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(restaurant, key, value)
    
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    
    return restaurant


@router.get("/menu")
def get_my_menu(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all menu items for owner's restaurant"""
    verify_owner(current_user)
    
    if not current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    statement = select(MenuItem).where(MenuItem.restaurant_id == current_user.restaurant_id)
    menu_items = session.exec(statement).all()
    
    return menu_items


@router.post("/menu", status_code=status.HTTP_201_CREATED)
def create_menu_item(
    menu_item: MenuItemCreateForOwner,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create new menu item for owner's restaurant"""
    verify_owner(current_user)
    
    if not current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    # Create menu item
    db_menu_item = MenuItem(
        **menu_item.model_dump(),
        restaurant_id=current_user.restaurant_id
    )
    
    session.add(db_menu_item)
    session.commit()
    session.refresh(db_menu_item)
    
    return db_menu_item


@router.put("/menu/{item_id}")
def update_menu_item(
    item_id: int,
    menu_item_data: MenuItemUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update menu item (owner can only update their own restaurant's items)"""
    verify_owner(current_user)
    
    menu_item = session.get(MenuItem, item_id)
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    # Verify ownership
    if menu_item.restaurant_id != current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own restaurant's menu items"
        )
    
    # Update fields
    update_data = menu_item_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(menu_item, key, value)
    
    session.add(menu_item)
    session.commit()
    session.refresh(menu_item)
    
    return menu_item


@router.delete("/menu/{item_id}")
def delete_menu_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete menu item"""
    verify_owner(current_user)
    
    menu_item = session.get(MenuItem, item_id)
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    # Verify ownership
    if menu_item.restaurant_id != current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own restaurant's menu items"
        )
    
    session.delete(menu_item)
    session.commit()
    
    return {"message": "Menu item deleted successfully"}


@router.get("/orders")
def get_my_orders(
    status_filter: OrderStatus = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all orders for owner's restaurant"""
    verify_owner(current_user)
    
    if not current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    statement = select(Order).where(Order.restaurant_id == current_user.restaurant_id)
    
    if status_filter:
        statement = statement.where(Order.status == status_filter)
    
    orders = session.exec(statement.order_by(Order.created_at.desc())).all()
    
    return orders


@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update order status (owner can only update their restaurant's orders)"""
    verify_owner(current_user)
    
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify ownership
    if order.restaurant_id != current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own restaurant's orders"
        )
    
    order.status = new_status
    order.updated_at = datetime.utcnow()
    
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return order


@router.get("/stats")
def get_restaurant_stats(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get statistics for owner's restaurant"""
    verify_owner(current_user)
    
    if not current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    # Get total orders
    total_orders = session.exec(
        select(Order).where(Order.restaurant_id == current_user.restaurant_id)
    ).all()
    
    # Get pending orders
    pending_orders = session.exec(
        select(Order).where(
            Order.restaurant_id == current_user.restaurant_id,
            Order.status == OrderStatus.PENDING
        )
    ).all()
    
    # Get total menu items
    total_menu_items = session.exec(
        select(MenuItem).where(MenuItem.restaurant_id == current_user.restaurant_id)
    ).all()
    
    # Calculate total revenue
    total_revenue = sum(order.total_amount for order in total_orders)
    
    return {
        "total_orders": len(total_orders),
        "pending_orders": len(pending_orders),
        "total_menu_items": len(total_menu_items),
        "total_revenue": total_revenue,
        "restaurant_id": current_user.restaurant_id
    }
