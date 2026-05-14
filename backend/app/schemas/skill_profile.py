"""
Skill Profile Response Schemas

Pydantic models for skill profile API responses.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class WeakKeyStatsResponse(BaseModel):
    """Stats for a single weak key."""
    character: str
    total_attempts: int
    total_errors: int
    error_rate: float
    error_distribution: Dict[str, int]
    recent_error_rate: float
    trend: str  # improving, stable, declining
    improvement_pct: Optional[float]


class ErrorPatternResponse(BaseModel):
    """A detected error pattern."""
    error_type: str
    total_occurrences: int
    percentage: float
    pattern_details: Dict[str, int]
    under_pressure: bool
    when_tired: bool
    sessions_with_error: int


class SkillInsightResponse(BaseModel):
    """A coaching insight."""
    insight_type: str  # strength, weakness, improvement, pattern, milestone
    title: str
    description: str
    metric_name: Optional[str]
    metric_value: Optional[float]
    recommendation: Optional[str]
    tone: str  # encouraging, cautionary, celebratory, honest
    priority: int


class UserSkillProfileResponse(BaseModel):
    """User's complete skill profile."""
    user_id: int
    
    # Overall Performance
    avg_wpm: float
    avg_accuracy: float
    total_sessions: int
    total_keystrokes: int
    total_errors: int
    
    # Trends
    improvement_week: Optional[float]
    improvement_month: Optional[float]
    consistency_score: float
    
    # Weak keys and error patterns
    weak_keys: Dict[str, Dict[str, float]]
    error_patterns: Dict[str, int]
    
    # Personal achievements
    best_wpm: Optional[float]
    best_accuracy: Optional[float]
    longest_streak: int
    current_streak: int
    
    # Metadata
    last_updated: datetime


class SkillHistoryPointResponse(BaseModel):
    """A single point in skill history."""
    session_id: int
    wpm: float
    accuracy: float
    total_sessions: int
    cumulative_wpm_avg: float
    cumulative_accuracy_avg: float
    wpm_change: Optional[float]
    accuracy_change: Optional[float]
    snapshot_date: datetime


class SkillHistoryResponse(BaseModel):
    """History of skill progression."""
    user_id: int
    period_days: int
    history: List[SkillHistoryPointResponse]
    
    # Trends
    overall_trend: str  # improving, stable, declining
    current_momentum: float  # Week-over-week improvement


class SkillSummaryResponse(BaseModel):
    """Quick summary of user skill (for dashboard)."""
    user_id: int
    
    # Key metrics
    avg_wpm: float
    avg_accuracy: float
    total_sessions: int
    
    # Status
    status: str  # beginner, intermediate, advanced
    confidence_level: float  # How sure are we about this profile (0-1)
    
    # Latest insights
    top_insight: Optional[SkillInsightResponse]
    weak_key: Optional[str]  # Most problematic character
    
    # Achievement
    milestone: Optional[str]  # Latest milestone
    achievement_level: float  # Overall progress (0-1)


class SkillComparisonResponse(BaseModel):
    """Compare user's metrics to benchmarks."""
    user_id: int
    
    # User metrics
    user_wpm: float
    user_accuracy: float
    user_sessions: int
    
    # Benchmarks
    avg_wpm_all_users: float
    avg_accuracy_all_users: float
    avg_sessions_all_users: int
    
    # Positioning
    wpm_percentile: float  # 0-100
    accuracy_percentile: float  # 0-100
    session_percentile: float  # 0-100
    
    # Insight
    comparison_text: str  # Human-readable comparison


class SkillRecommendationResponse(BaseModel):
    """Personalized recommendations based on skill profile."""
    user_id: int
    
    # Difficulty adjustment
    recommended_difficulty: int  # 1-10
    current_difficulty: int
    reason: str
    
    # Practice focus
    focus_areas: List[str]  # ["s", "p", "comma"] - characters to practice
    practice_method: str  # drill, sentences, mixed
    
    # Insights
    observations: List[str]  # What we notice about their typing
    strengths: List[str]  # What they're doing well
    growth_areas: List[str]  # What to improve
    
    # Motivation
    motivational_message: str  # Encouragement


class ProfileUpdateResponse(BaseModel):
    """Response after profile update."""
    user_id: int
    session_id: int
    
    # What changed
    profile_updated: bool
    metrics_changed: Dict[str, float]  # {metric_name: new_value}
    
    # New insights
    new_insights: List[SkillInsightResponse]
    updated_weak_keys: List[str]
    
    # Status
    profile_version: int
    last_updated: datetime
    next_update_estimated: datetime
