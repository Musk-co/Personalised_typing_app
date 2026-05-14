"""
Progress API Response Schemas

Pydantic models for progress endpoints.
"""

from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel


class AchievementResponse(BaseModel):
    """Achievement earned by user."""

    type: str
    title: str
    description: Optional[str]
    rarity: str  # common, rare, epic, legendary
    icon: Optional[str]
    earned_at: datetime

    class Config:
        from_attributes = True


class StreakResponse(BaseModel):
    """Current and personal best streaks."""

    type: str
    current_count: int
    longest_count: int
    last_activity_date: Optional[datetime]

    class Config:
        from_attributes = True


class MilestoneResponse(BaseModel):
    """Significant milestone achieved."""

    type: str
    title: str
    description: Optional[str]
    metric_name: Optional[str]
    metric_value: Optional[float]
    achieved_at: datetime
    celebration_shown: bool

    class Config:
        from_attributes = True


class TrendDataResponse(BaseModel):
    """Historical trend data for visualization."""

    date: datetime
    avg_wpm: float
    avg_accuracy: float
    best_wpm: Optional[float]
    best_accuracy: Optional[float]
    total_sessions: int
    week_improvement: Optional[float]  # % improvement
    month_improvement: Optional[float]  # % improvement

    class Config:
        from_attributes = True


class KeyboardHeatmapResponse(BaseModel):
    """Keyboard heatmap showing error rates per character."""

    heatmap: Dict[str, Dict]  # {char: {error_rate, color}}
    generated_at: datetime


class SkillProfileResponse(BaseModel):
    """User's current skill profile summary."""

    avg_wpm: float
    avg_accuracy: float
    best_wpm: Optional[float]
    best_accuracy: Optional[float]
    consistency_score: float
    total_sessions: int
    total_keystrokes: int
    improvement_week: Optional[float]
    improvement_month: Optional[float]


class ProgressStatsResponse(BaseModel):
    """Comprehensive progress statistics."""

    skill_profile: SkillProfileResponse
    achievements: List[AchievementResponse]
    streaks: List[StreakResponse]
    recent_milestones: List[MilestoneResponse]
    progress_trend: List[TrendDataResponse]

    class Config:
        from_attributes = True
