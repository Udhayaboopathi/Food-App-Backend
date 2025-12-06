"""
Restaurant router for restaurant CRUD operations
Handles restaurant discovery, search, and filtering
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, col
from typing import List, Optional

from ..core.database import get_session
from ..models import Restaurant, User, MenuItem, Review, Order, OrderItem
from ..schemas.restaurant import RestaurantCreate, RestaurantUpdate, RestaurantResponse
from .auth import get_current_user

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("", response_model=List[RestaurantResponse])
def get_restaurants(
    session: Session = Depends(get_session),
    city: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get list of restaurants with optional filters
    
    Args:
        session: Database session
        city: Filter by city
        cuisine: Filter by cuisine type
        search: Search in restaurant name
        min_rating: Minimum rating filter
        skip: Pagination offset
        limit: Pagination limit
    
    Returns:
        List of restaurants
    """
    statement = select(Restaurant).where(Restaurant.is_active == True)
    
    # Apply filters
    if city:
        statement = statement.where(col(Restaurant.city).ilike(f"%{city}%"))
    
    if cuisine:
        statement = statement.where(col(Restaurant.cuisine).ilike(f"%{cuisine}%"))
    
    if search:
        statement = statement.where(col(Restaurant.name).ilike(f"%{search}%"))
    
    if min_rating:
        statement = statement.where(Restaurant.rating >= min_rating)
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
    restaurants = session.exec(statement).all()
    return restaurants


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: int, session: Session = Depends(get_session)):
    """
    Get single restaurant by ID
    
    Args:
        restaurant_id: Restaurant ID
        session: Database session
    
    Returns:
        Restaurant data
    """
    restaurant = session.get(Restaurant, restaurant_id)
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    return restaurant


@router.post("", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
def create_restaurant(
    restaurant_data: RestaurantCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new restaurant (Admin only)
    
    Args:
        restaurant_data: Restaurant information
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        Created restaurant data
    """
    # Check admin role
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create restaurants"
        )
    
    new_restaurant = Restaurant(**restaurant_data.model_dump())
    session.add(new_restaurant)
    session.commit()
    session.refresh(new_restaurant)
    
    return new_restaurant


@router.patch("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(
    restaurant_id: int,
    restaurant_data: RestaurantUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update restaurant information (Admin only)
    
    Args:
        restaurant_id: Restaurant ID
        restaurant_data: Updated restaurant data
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated restaurant data
    """
    # Check admin role
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update restaurants"
        )
    
    restaurant = session.get(Restaurant, restaurant_id)
    
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


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(
    restaurant_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a restaurant (Admin only)
    
    Args:
        restaurant_id: Restaurant ID
        session: Database session
        current_user: Current authenticated user
    """
    # Check admin role
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete restaurants"
        )
    
    restaurant = session.get(Restaurant, restaurant_id)
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    
    # Delete all related data in the correct order
    # 1. Delete order items from orders at this restaurant
    orders_statement = select(Order).where(Order.restaurant_id == restaurant_id)
    orders = session.exec(orders_statement).all()
    for order in orders:
        order_items_statement = select(OrderItem).where(OrderItem.order_id == order.id)
        order_items = session.exec(order_items_statement).all()
        for order_item in order_items:
            session.delete(order_item)
    
    # 2. Delete orders
    for order in orders:
        session.delete(order)
    
    # 3. Delete reviews
    reviews_statement = select(Review).where(Review.restaurant_id == restaurant_id)
    reviews = session.exec(reviews_statement).all()
    for review in reviews:
        session.delete(review)
    
    # 4. Delete menu items
    menu_items_statement = select(MenuItem).where(MenuItem.restaurant_id == restaurant_id)
    menu_items = session.exec(menu_items_statement).all()
    for menu_item in menu_items:
        session.delete(menu_item)
    
    # 5. Flush all deletes before removing the restaurant
    session.flush()
    
    # 6. Finally delete the restaurant
    session.delete(restaurant)
    session.commit()
