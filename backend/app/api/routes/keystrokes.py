"""
Keystroke Recording Routes

Handles submission and processing of keystroke events with error classification.
Provides endpoints for:
- Batch keystroke submission
- Keystroke retrieval and analysis
- Error pattern extraction
- Weak key identification
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Keystroke, TypingSession as DBSession, User
from app.core.engine.error_detector import ErrorClassifier, DetailedError
from app.core.engine.evaluator import TypingEvaluator
from app.core.engine.skill_profile_service import SkillProfileService
from app.schemas.keystroke import (
    KeystrokeEventRequest,
    KeystrokeResponse,
    KeystrokeBatchRequest,
    KeystrokeBatchResponse,
    ErrorClassificationResponse,
    WeakKeyAnalysisResponse,
)

router = APIRouter(prefix="/api/v1/sessions", tags=["keystroke-recording"])


@router.post(
    "/{session_id}/keystrokes",
    response_model=KeystrokeBatchResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_keystrokes(
    session_id: int,
    batch: KeystrokeBatchRequest,
    db: Session = Depends(get_db),
) -> KeystrokeBatchResponse:
    """
    Submit a batch of keystroke events for a typing session.
    
    This endpoint:
    1. Validates keystroke events
    2. Classifies errors using Levenshtein distance
    3. Stores keystroke data with error classification
    4. Returns error details and metrics
    
    Args:
        session_id: ID of the typing session
        batch: Batch of keystroke events to process
        db: Database session
    
    Returns:
        KeystrokeBatchResponse with stored keystrokes and error classification
    
    Raises:
        404: If session not found
        422: If keystroke data invalid
    """
    
    # Verify session exists
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Initialize error classifier
    classifier = ErrorClassifier()
    
    # Get expected text from session
    expected_text = db_session.text_prompt or ""
    
    # Build typed text from keystroke batch
    typed_text = "".join(
        event.char for event in batch.events 
        if event.char not in ["\x08", "Backspace"]  # Exclude backspace
    )
    
    # Classify errors
    detailed_errors = classifier.classify_errors(expected_text, typed_text)
    
    # Store each keystroke
    stored_keystrokes = []
    for i, event in enumerate(batch.events):
        # Find corresponding error if any
        error_type = None
        expected_char = None
        
        if i < len(expected_text):
            expected_char = expected_text[i]
            if event.char != expected_char and event.char not in ["\x08", "Backspace"]:
                # Find error classification for this position
                for error in detailed_errors:
                    if error.position == i:
                        error_type = error.error_type.value
                        break
        
        # Create keystroke record
        keystroke = Keystroke(
            session_id=session_id,
            character=event.char,
            expected_character=expected_char,
            position=i,
            timestamp_ms=event.timestamp,
            is_correct=event.is_correct,
            error_type=error_type,
            context=batch.context or "",
        )
        
        db.add(keystroke)
        stored_keystrokes.append(keystroke)
    
    # Commit batch to database
    db.commit()
    
    # Calculate detailed metrics
    levenshtein_distance = classifier.levenshtein_distance(expected_text, typed_text)
    
    # Group errors by type
    error_by_type = {}
    for error in detailed_errors:
        error_type = error.error_type.value
        error_by_type[error_type] = error_by_type.get(error_type, 0) + 1
    
    # Trigger skill profile update for this session
    try:
        skill_service = SkillProfileService(db)
        skill_service.update_skill_profile_for_session(db_session.user_id, session_id)
    except Exception as e:
        # Log error but don't fail the keystroke submission
        print(f"Warning: Could not update skill profile: {str(e)}")
    
    # Build response
    return KeystrokeBatchResponse(
        session_id=session_id,
        keystrokes_stored=len(stored_keystrokes),
        error_classification={
            "total_errors": len(detailed_errors),
            "by_type": error_by_type,
            "levenshtein_distance": levenshtein_distance,
        },
        success=True,
    )


@router.get(
    "/{session_id}/keystrokes",
    response_model=List[KeystrokeResponse],
)
def get_session_keystrokes(
    session_id: int,
    db: Session = Depends(get_db),
    limit: int = 10000,
) -> List[KeystrokeResponse]:
    """
    Retrieve all keystroke events for a session.
    
    Args:
        session_id: ID of the typing session
        db: Database session
        limit: Maximum number of keystrokes to return
    
    Returns:
        List of keystroke events with error classification
    
    Raises:
        404: If session not found
    """
    
    # Verify session exists
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Fetch keystrokes
    keystrokes = db.query(Keystroke).filter(
        Keystroke.session_id == session_id
    ).order_by(Keystroke.position).limit(limit).all()
    
    return [
        KeystrokeResponse(
            session_id=keystroke.session_id,
            character=keystroke.character,
            expected_character=keystroke.expected_character,
            position=keystroke.position,
            timestamp_ms=keystroke.timestamp_ms,
            is_correct=keystroke.is_correct,
            error_type=keystroke.error_type,
            context=keystroke.context,
        )
        for keystroke in keystrokes
    ]


@router.get(
    "/{session_id}/keystrokes/analysis",
    response_model=ErrorClassificationResponse,
)
def analyze_session_errors(
    session_id: int,
    db: Session = Depends(get_db),
) -> ErrorClassificationResponse:
    """
    Analyze error patterns in a session's keystrokes.
    
    Provides detailed breakdown of:
    - Error types and counts
    - Levenshtein distance
    - Most common errors
    - Per-character analysis
    
    Args:
        session_id: ID of the typing session
        db: Database session
    
    Returns:
        Detailed error classification and analysis
    
    Raises:
        404: If session not found
    """
    
    # Verify session exists
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Fetch all keystrokes for session
    keystrokes = db.query(Keystroke).filter(
        Keystroke.session_id == session_id
    ).order_by(Keystroke.position).all()
    
    # Reconstruct typed text
    typed_text = "".join(
        k.character for k in keystrokes 
        if k.character not in ["\x08", "Backspace"]
    )
    
    # Classify errors
    classifier = ErrorClassifier()
    detailed_errors = classifier.classify_errors(
        db_session.text_prompt or "",
        typed_text
    )
    
    # Group errors by type
    error_by_type = {}
    for error in detailed_errors:
        error_type = error.error_type.value
        error_by_type[error_type] = error_by_type.get(error_type, 0) + 1
    
    # Group errors by character
    error_by_char = {}
    for error in detailed_errors:
        char = error.expected
        if char not in error_by_char:
            error_by_char[char] = {"count": 0, "types": {}}
        error_by_char[char]["count"] += 1
        error_type = error.error_type.value
        error_by_char[char]["types"][error_type] = (
            error_by_char[char]["types"].get(error_type, 0) + 1
        )
    
    return ErrorClassificationResponse(
        session_id=session_id,
        total_keystrokes=len(keystrokes),
        total_errors=len(detailed_errors),
        error_classification={
            "by_type": error_by_type,
            "levenshtein_distance": classifier.levenshtein_distance(
                db_session.text_prompt or "",
                typed_text
            ),
        },
        errors_by_character=error_by_char,
        detailed_errors=[
            {
                "position": e.position,
                "expected": e.expected,
                "actual": e.actual,
                "error_type": e.error_type.value,
                "timestamp_ms": e.timestamp_ms,
            }
            for e in detailed_errors[:50]  # Return first 50 for brevity
        ],
    )


@router.get(
    "/{session_id}/weak-keys",
    response_model=WeakKeyAnalysisResponse,
)
def analyze_weak_keys(
    session_id: int,
    db: Session = Depends(get_db),
) -> WeakKeyAnalysisResponse:
    """
    Identify weak keys (characters with high error rates) for a session.
    
    Returns:
    - Per-character error statistics
    - Error rates
    - Most problematic characters
    
    Args:
        session_id: ID of the typing session
        db: Database session
    
    Returns:
        Weak key analysis with per-character statistics
    
    Raises:
        404: If session not found
    """
    
    # Verify session exists
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Fetch all keystrokes for session
    keystrokes = db.query(Keystroke).filter(
        Keystroke.session_id == session_id
    ).order_by(Keystroke.position).all()
    
    # Analyze per-character statistics
    char_stats = {}
    for keystroke in keystrokes:
        char = keystroke.expected_character or keystroke.character
        
        if char not in char_stats:
            char_stats[char] = {
                "attempts": 0,
                "errors": 0,
                "error_types": {},
                "positions": [],
            }
        
        char_stats[char]["attempts"] += 1
        char_stats[char]["positions"].append(keystroke.position)
        
        if not keystroke.is_correct:
            char_stats[char]["errors"] += 1
            if keystroke.error_type:
                char_stats[char]["error_types"][keystroke.error_type] = (
                    char_stats[char]["error_types"].get(keystroke.error_type, 0) + 1
                )
    
    # Calculate error rates and sort
    weak_keys = []
    for char, stats in char_stats.items():
        error_rate = stats["errors"] / max(stats["attempts"], 1)
        weak_keys.append({
            "character": char,
            "attempts": stats["attempts"],
            "errors": stats["errors"],
            "error_rate": error_rate,
            "error_types": stats["error_types"],
            "positions": stats["positions"][:10],  # First 10 positions
        })
    
    # Sort by error rate (descending)
    weak_keys.sort(key=lambda x: x["error_rate"], reverse=True)
    
    return WeakKeyAnalysisResponse(
        session_id=session_id,
        total_characters=len(char_stats),
        weak_keys=weak_keys[:20],  # Return top 20
        perfect_keys=[
            char for char, stats in char_stats.items()
            if stats["errors"] == 0 and stats["attempts"] >= 5
        ],
    )
