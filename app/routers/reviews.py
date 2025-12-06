"""
Reviews router for restaurant review management
Handles review creation and retrieval
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from typing import List

from ..core.database import get_session
from ..models import Review, Restaurant, User, Order
from ..schemas.review import ReviewCreate, ReviewResponse
from .auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new review for a restaurant
    
    Args:
        review_data: Review information
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        Created review data
    """
    # Check if restaurant exists
    restaurant = session.get(Restaurant, review_data.restaurant_id)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    # Check if user has ordered from this restaurant
    statement = select(Order).where(
        Order.user_id == current_user.id,
        Order.restaurant_id == review_data.restaurant_id,
        Order.status == "delivered"
    )
    has_ordered = session.exec(statement).first()
    
    if not has_ordered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review restaurants you've ordered from"
        )
    
    # Create review
    new_review = Review(
        user_id=current_user.id,
        restaurant_id=review_data.restaurant_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    
    session.add(new_review)
    session.commit()
    
    # Update restaurant rating
    statement = select(func.avg(Review.rating)).where(Review.restaurant_id == review_data.restaurant_id)
    avg_rating = session.exec(statement).first()
    
    if avg_rating:
        restaurant.rating = round(float(avg_rating), 1)
        session.add(restaurant)
        session.commit()
    
    session.refresh(new_review)
    return new_review


@router.get("/restaurant/{restaurant_id}", response_model=List[ReviewResponse])
def get_restaurant_reviews(
    restaurant_id: int,
    session: Session = Depends(get_session)
):
    """
    Get all reviews for a restaurant
    
    Args:
        restaurant_id: Restaurant ID
        session: Database session
    
    Returns:
        List of reviews
    """
    statement = select(Review).where(Review.restaurant_id == restaurant_id).order_by(Review.created_at.desc())
    reviews = session.exec(statement).all()
    return reviews


@router.get("/user/me", response_model=List[ReviewResponse])
def get_my_reviews(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all reviews by current user
    
    Args:
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        List of user's reviews
    """
    statement = select(Review).where(Review.user_id == current_user.id).order_by(Review.created_at.desc())
    reviews = session.exec(statement).all()
    return reviews
