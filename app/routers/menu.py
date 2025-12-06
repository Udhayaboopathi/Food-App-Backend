"""
Menu router for menu item CRUD operations
Handles menu item management and filtering
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional

from ..core.database import get_session
from ..models import MenuItem, User
from ..schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from .auth import get_current_user

router = APIRouter(prefix="/menu", tags=["Menu Items"])


@router.get("/restaurant/{restaurant_id}", response_model=List[MenuItemResponse])
def get_menu_items(
    restaurant_id: int,
    session: Session = Depends(get_session),
    category: Optional[str] = Query(None),
    is_veg: Optional[bool] = Query(None),
    is_available: bool = Query(True)
):
    """
    Get menu items for a restaurant with optional filters
    
    Args:
        restaurant_id: Restaurant ID
        session: Database session
        category: Filter by category
        is_veg: Filter vegetarian items
        is_available: Show only available items
    
    Returns:
        List of menu items
    """
    statement = select(MenuItem).where(MenuItem.restaurant_id == restaurant_id)
    
    if category:
        statement = statement.where(MenuItem.category == category)
    
    if is_veg is not None:
        statement = statement.where(MenuItem.is_veg == is_veg)
    
    statement = statement.where(MenuItem.is_available == is_available)
    
    menu_items = session.exec(statement).all()
    return menu_items


@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(item_id: int, session: Session = Depends(get_session)):
    """
    Get single menu item by ID
    
    Args:
        item_id: Menu item ID
        session: Database session
    
    Returns:
        Menu item data
    """
    menu_item = session.get(MenuItem, item_id)
    
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    return menu_item


@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    item_data: MenuItemCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new menu item (Admin only)
    
    Args:
        item_data: Menu item information
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        Created menu item data
    """
    # Check admin role
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create menu items"
        )
    
    new_item = MenuItem(**item_data.model_dump())
    session.add(new_item)
    session.commit()
    session.refresh(new_item)
    
    return new_item


@router.patch("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    item_data: MenuItemUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update menu item (Admin only)
    
    Args:
        item_id: Menu item ID
        item_data: Updated menu item data
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated menu item data
    """
    # Check admin role
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update menu items"
        )
    
    menu_item = session.get(MenuItem, item_id)
    
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    # Update fields
    update_data = item_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(menu_item, key, value)
    
    session.add(menu_item)
    session.commit()
    session.refresh(menu_item)
    
    return menu_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    item_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a menu item (Admin only)
    
    Args:
        item_id: Menu item ID
        session: Database session
        current_user: Current authenticated user
    """
    # Check admin role
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete menu items"
        )
    
    menu_item = session.get(MenuItem, item_id)
    
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    session.delete(menu_item)
    session.commit()
