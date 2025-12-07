"""
Menu router for menu item CRUD operations (MongoDB version)
Handles menu item management and filtering
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from beanie import PydanticObjectId

from ..models.menu_item import MenuItem
from ..models.restaurant import Restaurant
from ..models.user import User
from ..schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from .auth import get_current_user

router = APIRouter(prefix="/menu", tags=["Menu Items"])


@router.get("/restaurant/{restaurant_id}")
async def get_menu_items(
    restaurant_id: str,
    category: Optional[str] = Query(None),
    is_veg: Optional[bool] = Query(None),
    is_available: bool = Query(True)
):
    """
    Get menu items for a restaurant with optional filters
    
    Args:
        restaurant_id: Restaurant ID
        category: Filter by category
        is_veg: Filter vegetarian items
        is_available: Show only available items
    
    Returns:
        List of menu items
    """
    query = {"restaurant_id": restaurant_id, "is_available": is_available}
    
    if category:
        query["category"] = category
    
    if is_veg is not None:
        query["is_veg"] = is_veg
    
    menu_items = await MenuItem.find(query).to_list()
    
    # Convert to dict with proper ID serialization
    result = []
    for item in menu_items:
        item_dict = item.model_dump(by_alias=False)
        item_dict["id"] = str(item.id)
        result.append(item_dict)
    
    return result


@router.get("/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(item_id: str):
    """
    Get a single menu item by ID
    
    Args:
        item_id: Menu item ID
    
    Returns:
        Menu item data
    """
    try:
        menu_item = await MenuItem.get(PydanticObjectId(item_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    # Convert to dict with proper ID serialization
    item_dict = menu_item.model_dump(by_alias=False)
    item_dict["id"] = str(menu_item.id)
    if menu_item.restaurant_id:
        item_dict["restaurant_id"] = str(menu_item.restaurant_id)
    
    return item_dict


@router.post("", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    menu_item_data: MenuItemCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new menu item (Restaurant Owner/Admin only)
    
    Args:
        menu_item_data: Menu item information
        current_user: Current authenticated user
    
    Returns:
        Created menu item data
    """
    # Check if restaurant exists
    try:
        restaurant = await Restaurant.get(PydanticObjectId(menu_item_data.restaurant_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    # Check authorization
    if current_user.role != "admin" and restaurant.owner_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurant owners and admins can add menu items"
        )
    
    new_menu_item = MenuItem(**menu_item_data.dict())
    await new_menu_item.insert()
    
    return new_menu_item


@router.put("/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(
    item_id: str,
    menu_item_data: MenuItemUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a menu item (Restaurant Owner/Admin only)
    
    Args:
        item_id: Menu item ID to update
        menu_item_data: Updated menu item data
        current_user: Current authenticated user
    
    Returns:
        Updated menu item data
    """
    try:
        menu_item = await MenuItem.get(PydanticObjectId(item_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    # Get restaurant to check ownership
    restaurant = await Restaurant.get(PydanticObjectId(menu_item.restaurant_id))
    
    # Check authorization
    if current_user.role != "admin" and restaurant.owner_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this menu item"
        )
    
    # Update fields
    update_data = menu_item_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(menu_item, field, value)
    
    await menu_item.save()
    
    # Convert to dict with proper ID serialization
    item_dict = menu_item.model_dump(by_alias=False)
    item_dict["id"] = str(menu_item.id)
    if menu_item.restaurant_id:
        item_dict["restaurant_id"] = str(menu_item.restaurant_id)
    
    return item_dict


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    item_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a menu item (Restaurant Owner/Admin only)
    
    Args:
        item_id: Menu item ID to delete
        current_user: Current authenticated user
    """
    try:
        menu_item = await MenuItem.get(PydanticObjectId(item_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    
    # Get restaurant to check ownership
    restaurant = await Restaurant.get(PydanticObjectId(menu_item.restaurant_id))
    
    # Check authorization
    if current_user.role != "admin" and restaurant.owner_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this menu item"
        )
    
    await menu_item.delete()
