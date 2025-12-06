"""
Admin Router
Admin endpoints for managing platform
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from ..core.database import get_session
from ..routers.auth import get_current_user
from ..models.user import User
from ..models.restaurant import Restaurant
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"])


class UpdateUserRole(BaseModel):
    """Schema for updating user role"""
    role: str
    restaurant_id: int | None = None


def verify_admin(current_user: User) -> User:
    """Verify user is an admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Admin role required."
        )
    return current_user


@router.get("/users")
def get_all_users(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all users (admin only)"""
    verify_admin(current_user)
    
    users = session.exec(select(User)).all()
    return users


@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    update_data: UpdateUserRole,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update user role and assign restaurant (admin only)"""
    verify_admin(current_user)
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update role
    user.role = update_data.role
    
    # Handle restaurant assignment
    # Remove old restaurant ownership if exists
    if user.restaurant_id:
        old_restaurant = session.get(Restaurant, user.restaurant_id)
        if old_restaurant and old_restaurant.owner_id == user_id:
            old_restaurant.owner_id = None
            session.add(old_restaurant)
    
    # Update restaurant assignment
    if update_data.restaurant_id:
        # Verify restaurant exists
        restaurant = session.get(Restaurant, update_data.restaurant_id)
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        # Check if restaurant already has an owner
        if restaurant.owner_id and restaurant.owner_id != user_id:
            existing_owner = session.get(User, restaurant.owner_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Restaurant '{restaurant.name}' already has an owner: {existing_owner.name if existing_owner else 'Unknown'}"
            )
        
        # If user is owner, check they don't already own another restaurant
        if user.role == "owner" and user.restaurant_id and user.restaurant_id != update_data.restaurant_id:
            current_restaurant = session.get(Restaurant, user.restaurant_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User already owns restaurant: {current_restaurant.name if current_restaurant else 'Unknown'}. Remove current assignment first."
            )
        
        user.restaurant_id = update_data.restaurant_id
        
        # If user is owner, update restaurant owner_id
        if user.role == "owner":
            restaurant.owner_id = user_id
            session.add(restaurant)
    else:
        # Remove restaurant assignment
        user.restaurant_id = None
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user


@router.get("/restaurants")
def get_all_restaurants(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all restaurants (admin only)"""
    verify_admin(current_user)
    
    restaurants = session.exec(select(Restaurant)).all()
    return restaurants
