"""
Restaurant router for restaurant CRUD operations (MongoDB version)
Handles restaurant discovery, search, and filtering
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from beanie import PydanticObjectId

from ..models.restaurant import Restaurant
from ..models.user import User
from ..schemas.restaurant import RestaurantCreate, RestaurantUpdate, RestaurantResponse
from .auth import get_current_user

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("")
async def get_restaurants(
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
        city: Filter by city
        cuisine: Filter by cuisine type
        search: Search in restaurant name
        min_rating: Minimum rating filter
        skip: Pagination offset
        limit: Pagination limit
    
    Returns:
        List of restaurants
    """
    query = {"is_active": True}
    
    # Apply filters
    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    
    if cuisine:
        query["cuisine"] = {"$regex": cuisine, "$options": "i"}
    
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    
    if min_rating is not None:
        query["rating"] = {"$gte": min_rating}
    
    restaurants = await Restaurant.find(query).skip(skip).limit(limit).to_list()
    
    # Convert to dict with proper ID serialization
    result = []
    for restaurant in restaurants:
        rest_dict = restaurant.model_dump(by_alias=False)
        rest_dict["id"] = str(restaurant.id)
        result.append(rest_dict)
    
    return result


@router.get("/{restaurant_id}")
async def get_restaurant(restaurant_id: str):
    """
    Get a single restaurant by ID
    
    Args:
        restaurant_id: Restaurant ID
    
    Returns:
        Restaurant data
    """
    try:
        restaurant = await Restaurant.get(PydanticObjectId(restaurant_id))
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
    
    # Convert to dict with proper ID serialization
    rest_dict = restaurant.model_dump(by_alias=False)
    rest_dict["id"] = str(restaurant.id)
    return rest_dict


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new restaurant (Admin/Owner only)
    
    Args:
        restaurant_data: Restaurant information
        current_user: Current authenticated user
    
    Returns:
        Created restaurant data
    """
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and owners can create restaurants"
        )
    
    new_restaurant = Restaurant(**restaurant_data.dict())
    if current_user.role == "owner":
        new_restaurant.owner_id = str(current_user.id)
    
    await new_restaurant.insert()
    
    # Convert to dict with proper ID serialization
    rest_dict = new_restaurant.model_dump(by_alias=False)
    rest_dict["id"] = str(new_restaurant.id)
    if new_restaurant.owner_id:
        rest_dict["owner_id"] = str(new_restaurant.owner_id)
    
    return rest_dict


@router.put("/{restaurant_id}")
async def update_restaurant(
    restaurant_id: str,
    restaurant_data: RestaurantUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a restaurant (Admin or Restaurant Owner only)
    
    Args:
        restaurant_id: Restaurant ID to update
        restaurant_data: Updated restaurant data
        current_user: Current authenticated user
    
    Returns:
        Updated restaurant data
    """
    try:
        restaurant = await Restaurant.get(PydanticObjectId(restaurant_id))
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
            detail="Not authorized to update this restaurant"
        )
    
    # Update fields
    update_data = restaurant_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(restaurant, field, value)
    
    await restaurant.save()
    
    # Convert to dict with proper ID serialization
    rest_dict = restaurant.model_dump(by_alias=False)
    rest_dict["id"] = str(restaurant.id)
    if restaurant.owner_id:
        rest_dict["owner_id"] = str(restaurant.owner_id)
    
    return rest_dict


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(
    restaurant_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a restaurant with cascade (Admin only)
    Deletes all related menu items, orders, and reviews
    
    Args:
        restaurant_id: Restaurant ID to delete
        current_user: Current authenticated user
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete restaurants"
        )
    
    try:
        restaurant = await Restaurant.get(PydanticObjectId(restaurant_id))
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
    
    # CASCADE DELETE - Delete all related data
    from ..models.menu_item import MenuItem
    from ..models.order import Order
    from ..models.review import Review
    
    # 1. Delete all menu items for this restaurant
    menu_items = await MenuItem.find({"restaurant_id": restaurant_id}).to_list()
    for item in menu_items:
        await item.delete()
    
    # 2. Delete all orders for this restaurant
    orders = await Order.find({"restaurant_id": restaurant_id}).to_list()
    for order in orders:
        await order.delete()
    
    # 3. Delete all reviews for this restaurant
    reviews = await Review.find({"restaurant_id": restaurant_id}).to_list()
    for review in reviews:
        await review.delete()
    
    # 4. Clear owner assignment if exists
    if restaurant.owner_id:
        owner = await User.get(PydanticObjectId(restaurant.owner_id))
        if owner:
            owner.restaurant_id = None
            await owner.save()
    
    # 5. Finally delete the restaurant
    await restaurant.delete()
    
    print(f"🗑️ Deleted restaurant '{restaurant.name}' and all related data (menu items, orders, reviews)")
