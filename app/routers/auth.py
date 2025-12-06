"""
Authentication router for user registration and login
Handles JWT token generation and user authentication
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import Annotated

from ..core.database import get_session
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from ..models import User
from ..schemas.auth import UserLogin, UserRegister, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session)
) -> User:
    """
    Dependency to get the current authenticated user
    Validates JWT token and returns user object
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, session: Session = Depends(get_session)):
    """
    Register a new user account
    
    Args:
        user_data: User registration information
        session: Database session
    
    Returns:
        Created user data
    """
    # Check if user already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hashed_password,
        address=user_data.address
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    """
    Login with email and password
    Returns JWT access and refresh tokens
    
    Args:
        form_data: OAuth2 compatible form with username (email) and password
        session: Database session
    
    Returns:
        JWT tokens
    """
    # Find user by email
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User data
    """
    return current_user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user_profile(
    user_id: int,
    name: str | None = None,
    phone: str | None = None,
    address: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update user profile information
    
    Args:
        user_id: User ID to update
        name: New name
        phone: New phone number
        address: New address
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        Updated user data
    """
    # Only allow users to update their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    # Update user fields
    if name is not None:
        current_user.name = name
    if phone is not None:
        current_user.phone = phone
    if address is not None:
        current_user.address = address
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return current_user


@router.put("/users/{user_id}/password")
def reset_password(
    user_id: int,
    old_password: str,
    new_password: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Reset user password
    
    Args:
        user_id: User ID to update password
        old_password: Current password for verification
        new_password: New password
        session: Database session
        current_user: Current authenticated user
    
    Returns:
        Success message
    """
    # Only allow users to update their own password
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this password"
        )
    
    # Verify old password
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    
    session.add(current_user)
    session.commit()
    
    return {"message": "Password updated successfully"}
