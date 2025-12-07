"""
Owner router for restaurant owner management
Handles owner's restaurant, menu, and order management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from beanie import PydanticObjectId

from ..models.restaurant import Restaurant
from ..models.menu_item import MenuItem
from ..models.order import Order
from ..models.user import User
from ..schemas.restaurant import RestaurantUpdate
from ..schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemCreateForOwner
from .auth import get_current_user

router = APIRouter(prefix="/owner", tags=["Owner"])


def get_current_owner(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure current user is an owner"""
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Owner role required."
        )
    return current_user


@router.get("/restaurant")
async def get_owner_restaurant(owner: User = Depends(get_current_owner)):
    """
    Get the restaurant owned by the current owner
    
    Returns:
        Restaurant details with string IDs
    """
    if not owner.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    try:
        restaurant = await Restaurant.get(PydanticObjectId(owner.restaurant_id))
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        # Serialize ObjectId to string
        restaurant_dict = restaurant.model_dump(by_alias=False)
        restaurant_dict["id"] = str(restaurant.id)
        if restaurant_dict.get("owner_id"):
            restaurant_dict["owner_id"] = str(restaurant_dict["owner_id"])
        
        return restaurant_dict
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch restaurant: {str(e)}"
        )


@router.put("/restaurant")
async def update_owner_restaurant(
    restaurant_data: RestaurantUpdate,
    owner: User = Depends(get_current_owner)
):
    """
    Update the owner's restaurant details
    
    Args:
        restaurant_data: Updated restaurant information
        
    Returns:
        Updated restaurant with string IDs
    """
    if not owner.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    try:
        restaurant = await Restaurant.get(PydanticObjectId(owner.restaurant_id))
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        # Update only provided fields
        update_data = restaurant_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(restaurant, field, value)
        
        await restaurant.save()
        
        # Serialize ObjectId to string
        restaurant_dict = restaurant.model_dump(by_alias=False)
        restaurant_dict["id"] = str(restaurant.id)
        if restaurant_dict.get("owner_id"):
            restaurant_dict["owner_id"] = str(restaurant_dict["owner_id"])
        
        return restaurant_dict
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update restaurant: {str(e)}"
        )


@router.get("/stats")
async def get_owner_stats(owner: User = Depends(get_current_owner)):
    """
    Get statistics for the owner's restaurant
    
    Returns:
        Restaurant statistics including orders, revenue, etc.
    """
    if not owner.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    try:
        restaurant_id = PydanticObjectId(owner.restaurant_id)
        
        # Get total orders
        total_orders = await Order.find(
            Order.restaurant_id == str(restaurant_id)
        ).count()
        
        # Get pending orders
        pending_orders = await Order.find(
            Order.restaurant_id == str(restaurant_id),
            Order.status == "pending"
        ).count()
        
        # Get preparing orders
        preparing_orders = await Order.find(
            Order.restaurant_id == str(restaurant_id),
            Order.status == "preparing"
        ).count()
        
        # Get completed orders
        completed_orders = await Order.find(
            Order.restaurant_id == str(restaurant_id),
            Order.status == "delivered"
        ).count()
        
        # Calculate total revenue (from completed orders)
        completed_order_list = await Order.find(
            Order.restaurant_id == str(restaurant_id),
            Order.status == "delivered"
        ).to_list()
        
        total_revenue = sum(order.total_amount for order in completed_order_list)
        
        # Get menu items count
        menu_items_count = await MenuItem.find(
            MenuItem.restaurant_id == str(restaurant_id)
        ).count()
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "preparing_orders": preparing_orders,
            "completed_orders": completed_orders,
            "total_revenue": total_revenue,
            "menu_items": menu_items_count
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


@router.get("/orders")
async def get_owner_orders(owner: User = Depends(get_current_owner)):
    """
    Get all orders for the owner's restaurant
    
    Returns:
        List of orders with string IDs
    """
    if not owner.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    try:
        restaurant_id = PydanticObjectId(owner.restaurant_id)
        
        orders = await Order.find(
            Order.restaurant_id == str(restaurant_id)
        ).sort(-Order.created_at).to_list()
        
        # Serialize ObjectIds to strings
        serialized_orders = []
        for order in orders:
            order_dict = order.model_dump(by_alias=False)
            order_dict["id"] = str(order.id)
            if order_dict.get("user_id"):
                order_dict["user_id"] = str(order_dict["user_id"])
            if order_dict.get("restaurant_id"):
                order_dict["restaurant_id"] = str(order_dict["restaurant_id"])
            if order_dict.get("delivery_agent_id"):
                order_dict["delivery_agent_id"] = str(order_dict["delivery_agent_id"])
            serialized_orders.append(order_dict)
        
        return serialized_orders
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch orders: {str(e)}"
        )


@router.get("/menu")
async def get_owner_menu(owner: User = Depends(get_current_owner)):
    """
    Get all menu items for the owner's restaurant
    
    Returns:
        List of menu items with string IDs
    """
    if not owner.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    try:
        restaurant_id = PydanticObjectId(owner.restaurant_id)
        
        menu_items = await MenuItem.find(
            MenuItem.restaurant_id == str(restaurant_id)
        ).to_list()
        
        # Serialize ObjectIds to strings
        serialized_menu = []
        for item in menu_items:
            item_dict = item.model_dump(by_alias=False)
            item_dict["id"] = str(item.id)
            if item_dict.get("restaurant_id"):
                item_dict["restaurant_id"] = str(item_dict["restaurant_id"])
            serialized_menu.append(item_dict)
        
        return serialized_menu
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch menu: {str(e)}"
        )


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    new_status: str = Query(..., description="New order status"),
    owner: User = Depends(get_current_owner)
):
    """
    Update order status for owner's restaurant orders
    
    Args:
        order_id: Order ID
        new_status: New status (pending, preparing, ready, out_for_delivery, delivered, cancelled)
        
    Returns:
        Updated order with string IDs
    """
    if not owner.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    try:
        order = await Order.get(PydanticObjectId(order_id))
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Verify order belongs to owner's restaurant
        if order.restaurant_id != owner.restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This order does not belong to your restaurant"
            )
        
        # Update status
        order.status = new_status
        await order.save()
        
        # Serialize ObjectId to string
        order_dict = order.model_dump(by_alias=False)
        order_dict["id"] = str(order.id)
        if order_dict.get("user_id"):
            order_dict["user_id"] = str(order_dict["user_id"])
        if order_dict.get("restaurant_id"):
            order_dict["restaurant_id"] = str(order_dict["restaurant_id"])
        if order_dict.get("delivery_agent_id"):
            order_dict["delivery_agent_id"] = str(order_dict["delivery_agent_id"])
        
        return order_dict
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update order status: {str(e)}"
        )


@router.post("/menu", status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    menu_item_data: MenuItemCreateForOwner,
    owner: User = Depends(get_current_owner)
):
    """
    Create a new menu item for owner's restaurant
    
    Args:
        menu_item_data: Menu item information (restaurant_id auto-assigned)
        
    Returns:
        Created menu item with string IDs
    """
    if not owner.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    try:
        # Create menu item with owner's restaurant_id
        item_dict = menu_item_data.model_dump()
        item_dict["restaurant_id"] = owner.restaurant_id
        
        new_menu_item = MenuItem(**item_dict)
        await new_menu_item.insert()
        
        # Serialize ObjectId to string
        item_dict = new_menu_item.model_dump(by_alias=False)
        item_dict["id"] = str(new_menu_item.id)
        if item_dict.get("restaurant_id"):
            item_dict["restaurant_id"] = str(item_dict["restaurant_id"])
        
        return item_dict
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create menu item: {str(e)}"
        )


@router.put("/menu/{item_id}")
async def update_menu_item(
    item_id: str,
    menu_item_data: MenuItemUpdate,
    owner: User = Depends(get_current_owner)
):
    """
    Update a menu item in owner's restaurant
    
    Args:
        item_id: Menu item ID to update
        menu_item_data: Updated menu item data
        
    Returns:
        Updated menu item with string IDs
    """
    if not owner.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    try:
        menu_item = await MenuItem.get(PydanticObjectId(item_id))
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        # Verify menu item belongs to owner's restaurant
        if menu_item.restaurant_id != owner.restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This menu item does not belong to your restaurant"
            )
        
        # Update fields
        update_data = menu_item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(menu_item, field, value)
        
        await menu_item.save()
        
        # Serialize ObjectId to string
        item_dict = menu_item.model_dump(by_alias=False)
        item_dict["id"] = str(menu_item.id)
        if item_dict.get("restaurant_id"):
            item_dict["restaurant_id"] = str(item_dict["restaurant_id"])
        
        return item_dict
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update menu item: {str(e)}"
        )


@router.delete("/menu/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    item_id: str,
    owner: User = Depends(get_current_owner)
):
    """
    Delete a menu item from owner's restaurant
    
    Args:
        item_id: Menu item ID to delete
    """
    if not owner.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant assigned to this owner"
        )
    
    try:
        menu_item = await MenuItem.get(PydanticObjectId(item_id))
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        # Verify menu item belongs to owner's restaurant
        if menu_item.restaurant_id != owner.restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This menu item does not belong to your restaurant"
            )
        
        await menu_item.delete()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete menu item: {str(e)}"
        )
