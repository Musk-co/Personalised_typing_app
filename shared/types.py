"""Shared type definitions."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """User type."""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime


@dataclass
class TypingMetrics:
    """Typing metrics type."""
    wpm: float
    accuracy: float
    errors: int
    key_presses: int


@dataclass
class TypingSession:
    """Typing session type."""
    id: int
    user_id: int
    test_type: str
    difficulty_level: int
    metrics: TypingMetrics
    status: str
    started_at: datetime
    ended_at: Optional[datetime]


@dataclass
class AdapterRecommendation:
    """Adapter recommendation type."""
    next_difficulty: int
    focus_areas: list[str]
    reason: str
    confidence: float
