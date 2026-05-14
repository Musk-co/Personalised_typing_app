"""
Exercise Response Schemas

Pydantic models for exercise-related API responses.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AdaptationRecommendationResponse(BaseModel):
    """Recommendation from adaptation engine."""
    next_difficulty: int = Field(..., ge=1, le=10)
    difficulty_change: str  # increase, maintain, decrease
    exercise_type: str
    rationale: str


class ExerciseResponse(BaseModel):
    """A generated exercise."""
    exercise_id: int
    text_prompt: str
    exercise_type: str
    difficulty: int
    focus_chars: List[str]
    description: str
    expected_duration_seconds: int
    adaptation_recommendation: Optional[AdaptationRecommendationResponse] = None
    generated_at: datetime


class ExerciseGenerateRequest(BaseModel):
    """Request to generate an exercise."""
    difficulty: Optional[int] = Field(None, ge=1, le=10)
    exercise_type: Optional[str] = None
    duration_seconds: Optional[int] = Field(None, ge=10)


class ExerciseAttemptRequest(BaseModel):
    """Request to submit exercise attempt."""
    session_id: Optional[int] = None
    accuracy: float = Field(..., ge=0, le=100)
    wpm: float = Field(..., ge=0)
    errors: int = Field(default=0, ge=0)
    duration_seconds: int = Field(..., ge=1)
    difficulty_felt: Optional[str] = None  # easy, fair, hard, too_hard
    confidence_level: Optional[int] = Field(None, ge=1, le=10)


class ExerciseAttemptResponse(BaseModel):
    """Response to exercise submission."""
    attempt_id: int
    exercise_id: int
    accuracy: float
    wpm: float
    errors: int
    duration_seconds: int
    was_successful: bool
    feedback: str
    next_recommendation: Optional[AdaptationRecommendationResponse] = None


class PlacementTestStartResponse(BaseModel):
    """Response when starting placement test."""
    test_id: int
    user_id: int
    instructions: str
    exercises: List[Dict]  # [{"level": "easy", "text": "...", "description": "...", "expected_duration_seconds": 30}]
    created_at: datetime


class PlacementTestSubmitRequest(BaseModel):
    """Request to submit placement test results."""
    easy_accuracy: float = Field(..., ge=0, le=100)
    easy_wpm: float = Field(..., ge=0)
    easy_duration: int = Field(..., ge=1)
    
    medium_accuracy: float = Field(..., ge=0, le=100)
    medium_wpm: float = Field(..., ge=0)
    medium_duration: int = Field(..., ge=1)
    
    hard_accuracy: float = Field(..., ge=0, le=100)
    hard_wpm: float = Field(..., ge=0)
    hard_duration: int = Field(..., ge=1)


class PlacementTestResultResponse(BaseModel):
    """Response after placement test submission."""
    test_id: int
    classified_level: str  # beginner, intermediate, advanced
    recommended_difficulty: int
    confidence: float
    starting_exercise_type: str
    message: str
