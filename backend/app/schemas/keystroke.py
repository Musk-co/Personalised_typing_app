"""
Keystroke Request/Response Schemas

Pydantic models for keystroke submission, analysis, and error classification.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class KeystrokeEventRequest(BaseModel):
    """Single keystroke event from frontend."""
    
    char: str = Field(..., description="Character typed")
    timestamp: float = Field(..., description="Timestamp in milliseconds")
    position: int = Field(..., description="Position in text")
    expected: str = Field(..., description="Expected character at this position")
    is_correct: bool = Field(..., description="Whether keystroke is correct")
    elapsed_ms: Optional[float] = Field(None, description="Elapsed time in ms")


class KeystrokeBatchRequest(BaseModel):
    """Batch of keystroke events to submit."""
    
    events: List[KeystrokeEventRequest] = Field(..., description="List of keystroke events")
    context: Optional[str] = Field(None, description="Additional context")
    test_duration_ms: Optional[float] = Field(None, description="Total test duration")


class KeystrokeResponse(BaseModel):
    """Response model for a single keystroke."""
    
    session_id: str
    character: str
    expected_character: Optional[str]
    position: int
    timestamp_ms: float
    is_correct: bool
    error_type: Optional[str] = None
    context: Optional[str] = None


class KeystrokeBatchResponse(BaseModel):
    """Response model for keystroke batch submission."""
    
    session_id: str
    keystrokes_stored: int
    error_classification: Dict[str, Any] = Field(
        ...,
        description="Error classification with types and Levenshtein distance"
    )
    success: bool


class ErrorClassificationResponse(BaseModel):
    """Detailed error analysis for a session."""
    
    session_id: str
    total_keystrokes: int
    total_errors: int
    error_classification: Dict[str, Any] = Field(
        ...,
        description="Error breakdown by type and Levenshtein distance"
    )
    errors_by_character: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Per-character error analysis"
    )
    detailed_errors: List[Dict[str, Any]] = Field(
        ...,
        description="List of individual error details (first 50)"
    )


class WeakKeyAnalysisResponse(BaseModel):
    """Weak key analysis for a session."""
    
    session_id: str
    total_characters: int
    weak_keys: List[Dict[str, Any]] = Field(
        ...,
        description="Characters with highest error rates"
    )
    perfect_keys: List[str] = Field(
        ...,
        description="Characters typed perfectly (≥5 attempts)"
    )


class SessionMetricsResponse(BaseModel):
    """Overall session metrics."""
    
    session_id: str
    wpm: float
    accuracy: float
    total_keystrokes: int
    total_errors: int
    error_types: Dict[str, int]
    levenshtein_distance: int
    weak_keys: List[str]
    duration_ms: float
