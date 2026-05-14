"""
Authentication endpoints.
Handles user registration, login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.db.models import User
from app.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: User's email address
    - **username**: Unique username
    - **password**: Minimum 8 characters
    - **full_name**: Optional full name
    """
    # TODO: Check if user already exists
    # TODO: Hash password before storing
    # TODO: Create JWT token
    # TODO: Return user and token
    pass


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token.
    
    - **email**: User's email
    - **password**: User's password
    """
    # TODO: Validate credentials
    # TODO: Create JWT token
    # TODO: Return user and token
    pass


@router.post("/logout")
async def logout():
    """
    Logout user (client-side token invalidation).
    """
    # TODO: Implement token blacklist or client-side handling
    pass


@router.post("/refresh")
async def refresh_token():
    """
    Refresh JWT token.
    """
    # TODO: Validate current token
    # TODO: Issue new token
    pass
