"""
User profile and preference endpoints.
Handles user data, settings, and preferences.
"""

from fastapi import APIRouter, Depends

from app.api.schemas import UserResponse
from app.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users")


@router.get("/me", response_model=UserResponse)
async def get_current_user(db: Session = Depends(get_db)):
    """
    Get current user's profile.
    Requires authentication.
    """
    # TODO: Get user from token
    # TODO: Return user profile
    pass


@router.put("/me")
async def update_profile(
    profile_update: dict,
    db: Session = Depends(get_db),
):
    """
    Update current user's profile.
    
    Can update:
    - full_name
    - preferences (theme, notifications, etc.)
    """
    # TODO: Get user from token
    # TODO: Validate and update profile
    # TODO: Return updated user
    pass


@router.get("/{user_id}")
async def get_user_public_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Get public user profile (limited data).
    No authentication required.
    """
    # TODO: Get user by ID
    # TODO: Return public profile (username, stats, etc.)
    pass


@router.post("/preferences")
async def set_user_preferences(
    preferences: dict,
    db: Session = Depends(get_db),
):
    """
    Set user preferences.
    
    Preferences include:
    - theme (light/dark)
    - notifications (enabled/disabled)
    - language
    - keyboard layout
    """
    # TODO: Get user from token
    # TODO: Store preferences
    # TODO: Return updated preferences
    pass


@router.get("/preferences")
async def get_user_preferences(db: Session = Depends(get_db)):
    """
    Get user preferences.
    """
    # TODO: Get user from token
    # TODO: Return preferences
    pass
