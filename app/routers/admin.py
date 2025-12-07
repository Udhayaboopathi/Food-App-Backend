"""
Admin Router - MongoDB Version
Admin endpoints for managing platform
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from beanie import PydanticObjectId

from ..routers.auth import get_current_user
from ..models.user import User
from ..models.restaurant import Restaurant

router = APIRouter(prefix="/admin", tags=["Admin"])


class UpdateUserRole(BaseModel):
    """Schema for updating user role"""
    role: str
    restaurant_id: str | None = None


def verify_admin(current_user: User) -> User:
    """Verify user is an admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Admin role required."
        )
    return current_user


@router.get("/users")
async def get_all_users(
    current_user: User = Depends(get_current_user)
):
    """Get all users (admin only)"""
    verify_admin(current_user)
    
    users = await User.find_all().to_list()
    
    # Manual serialization
    result = []
    for user in users:
        user_dict = user.model_dump(by_alias=False)
        user_dict["id"] = str(user.id)
        if user.restaurant_id:
            user_dict["restaurant_id"] = str(user.restaurant_id)
        result.append(user_dict)
    
    return result


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    update_data: UpdateUserRole,
    current_user: User = Depends(get_current_user)
):
    """Update user role and assign restaurant (admin only)"""
    verify_admin(current_user)
    
    try:
        user_obj_id = PydanticObjectId(user_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = await User.get(user_obj_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Handle restaurant assignment
    # Remove old restaurant ownership if exists
    if user.restaurant_id:
        old_restaurant = await Restaurant.get(PydanticObjectId(user.restaurant_id))
        if old_restaurant and str(old_restaurant.owner_id) == user_id:
            old_restaurant.owner_id = None
            await old_restaurant.save()
    
    # Update restaurant assignment
    if update_data.restaurant_id:
        try:
            restaurant_obj_id = PydanticObjectId(update_data.restaurant_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid restaurant ID format"
            )
        
        # Verify restaurant exists
        restaurant = await Restaurant.get(restaurant_obj_id)
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        # Check if restaurant already has a different owner
        if restaurant.owner_id and str(restaurant.owner_id) != user_id:
            # Remove the existing owner
            existing_owner = await User.get(PydanticObjectId(restaurant.owner_id))
            if existing_owner:
                existing_owner.restaurant_id = None
                existing_owner.role = "user"  # Demote previous owner to user
                await existing_owner.save()
                print(f"🔄 Removed {existing_owner.name} as owner of {restaurant.name}")
        
        # Automatically set role to "owner" when restaurant is assigned
        user.role = "owner"
        user.restaurant_id = update_data.restaurant_id
        
        # Update restaurant owner_id
        restaurant.owner_id = user_id
        await restaurant.save()
        
        print(f"✅ Assigned {user.name} as owner of {restaurant.name}")
    else:
        # If no restaurant assigned, use the provided role (or keep existing)
        user.role = update_data.role
        user.restaurant_id = None
    
    await user.save()
    
    # Manual serialization
    user_dict = user.model_dump(by_alias=False)
    user_dict["id"] = str(user.id)
    if user.restaurant_id:
        user_dict["restaurant_id"] = str(user.restaurant_id)
    
    return user_dict


@router.get("/restaurants")
async def get_all_restaurants(
    current_user: User = Depends(get_current_user)
):
    """Get all restaurants with owner details (admin only)"""
    verify_admin(current_user)
    
    restaurants = await Restaurant.find_all().to_list()
    
    # Manual serialization with owner details
    result = []
    for restaurant in restaurants:
        rest_dict = restaurant.model_dump(by_alias=False)
        rest_dict["id"] = str(restaurant.id)
        
        # Add owner details
        if restaurant.owner_id:
            rest_dict["owner_id"] = str(restaurant.owner_id)
            try:
                owner = await User.get(PydanticObjectId(restaurant.owner_id))
                if owner:
                    rest_dict["owner_name"] = owner.name
                    rest_dict["owner_email"] = owner.email
                else:
                    rest_dict["owner_name"] = None
                    rest_dict["owner_email"] = None
            except:
                rest_dict["owner_name"] = None
                rest_dict["owner_email"] = None
        else:
            rest_dict["owner_id"] = None
            rest_dict["owner_name"] = None
            rest_dict["owner_email"] = None
        
        result.append(rest_dict)
    
    return result


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a user (admin only)"""
    verify_admin(current_user)
    
    try:
        user_obj_id = PydanticObjectId(user_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = await User.get(user_obj_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting admin users
    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete admin users"
        )
    
    # Prevent deleting yourself
    if str(user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete your own account"
        )
    
    # If user owns a restaurant, remove ownership
    if user.restaurant_id:
        restaurant = await Restaurant.get(PydanticObjectId(user.restaurant_id))
        if restaurant and str(restaurant.owner_id) == user_id:
            restaurant.owner_id = None
            await restaurant.save()
    
    email = user.email
    await user.delete()
    
    return {"message": f"User {email} deleted successfully"}


@router.get("/orders")
async def get_all_orders(
    current_user: User = Depends(get_current_user)
):
    """Get all orders in the system (admin only)"""
    verify_admin(current_user)
    
    from ..models.order import Order
    
    orders = await Order.find_all().to_list()
    
    # Manual serialization
    result = []
    for order in orders:
        order_dict = order.model_dump(by_alias=False)
        order_dict["id"] = str(order.id)
        if order.user_id:
            order_dict["user_id"] = str(order.user_id)
        if order.restaurant_id:
            order_dict["restaurant_id"] = str(order.restaurant_id)
        result.append(order_dict)
    
    return result


@router.get("/restaurants")
async def get_all_restaurants(
    current_user: User = Depends(get_current_user)
):
    """Get all restaurants (admin only)"""
    verify_admin(current_user)
    
    restaurants = await Restaurant.find_all().to_list()
    
    # Manual serialization
    result = []
    for restaurant in restaurants:
        restaurant_dict = restaurant.model_dump(by_alias=False)
        restaurant_dict["id"] = str(restaurant.id)
        if restaurant.owner_id:
            restaurant_dict["owner_id"] = str(restaurant.owner_id)
        result.append(restaurant_dict)
    
    return result
