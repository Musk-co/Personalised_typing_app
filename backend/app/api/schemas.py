"""
Pydantic schemas for request/response validation.
Ensures type safety and API documentation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ============= Authentication Schemas =============
class UserBase(BaseModel):
    """Base user information."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation request."""

    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response (no password)."""

    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============= Typing Session Schemas =============
class TypingMetrics(BaseModel):
    """Metrics for a typing session."""

    wpm: float = Field(..., description="Words per minute")
    accuracy: float = Field(..., ge=0, le=100, description="Accuracy percentage")
    errors: int = Field(..., ge=0, description="Number of errors")
    key_presses: int = Field(..., ge=0, description="Total key presses")


class SessionCreate(BaseModel):
    """Create a new typing session."""

    test_type: str = Field(..., description="Type of test (e.g., 'standard', 'coding')")
    difficulty_level: int = Field(
        default=1, ge=1, le=10, description="Difficulty level 1-10"
    )
    custom_text: Optional[str] = None
    adapter_config: Optional[dict] = Field(
        default=None, description="Adapter-specific configuration"
    )


class SessionUpdate(BaseModel):
    """Update a typing session."""

    metrics: TypingMetrics
    status: str = Field(..., description="'in_progress', 'completed', 'paused'")
    end_time: Optional[datetime] = None


class SessionResponse(BaseModel):
    """Typing session response."""

    id: int
    user_id: int
    test_type: str
    difficulty_level: int
    metrics: TypingMetrics
    status: str
    started_at: datetime
    ended_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Adaptive Schemas =============
class AdapterConfig(BaseModel):
    """Configuration for typing adaptation engine."""

    adapter_type: str = Field(..., description="'rule_based' or 'ml'")
    parameters: dict = Field(default_factory=dict, description="Adapter-specific params")


class AdapterRecommendation(BaseModel):
    """Recommendation from adapter engine."""

    next_difficulty: int = Field(..., ge=1, le=10)
    focus_areas: list[str] = Field(
        default_factory=list, description="Areas to focus on"
    )
    reason: str
    confidence: float = Field(..., ge=0, le=1)


# ============= Analytics Schemas =============
class UserStats(BaseModel):
    """User statistics over a period."""

    total_sessions: int
    avg_wpm: float
    avg_accuracy: float
    best_wpm: float
    total_errors: int
    improvement_trend: Optional[float] = None


class ProgressData(BaseModel):
    """Progress data for charting."""

    date: datetime
    wpm: float
    accuracy: float


# ============= Leaderboard Schemas =============
class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""

    rank: int
    user_id: int
    username: str
    best_wpm: float
    avg_accuracy: float
    total_sessions: int
