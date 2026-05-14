"""
Exercise Routes

Endpoints for generating, retrieving, and tracking exercises.
Provides the adaptive training workflow.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import (
    Exercise, 
    ExerciseAttempt, 
    PlacementTest,
    User,
    UserSkillProfile,
    TypingSession,
)
from app.core.engine.exercise_generator import ExerciseGenerator, ExerciseType
from app.core.engine.adaptation_engine import (
    RuleBasedAdaptationEngine,
    AdaptationEngineFactory,
    UserLevel,
)
from app.core.engine.placement_test import PlacementTestService
from app.services.progress_tracker import ProgressTracker
from app.schemas.exercise import (
    ExerciseResponse,
    ExerciseGenerateRequest,
    ExerciseAttemptRequest,
    ExerciseAttemptResponse,
    PlacementTestStartResponse,
    PlacementTestSubmitRequest,
    PlacementTestResultResponse,
    AdaptationRecommendationResponse,
)

router = APIRouter(prefix="/api/v1", tags=["exercises"])


@router.post(
    "/users/{user_id}/exercises/generate",
    response_model=ExerciseResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_next_exercise(
    user_id: int,
    request: Optional[ExerciseGenerateRequest] = None,
    db: Session = Depends(get_db),
) -> ExerciseResponse:
    """
    Generate a fresh exercise tailored to user's weaknesses.
    
    Generates new exercise from live skill data - never static.
    Uses adaptation engine to determine difficulty and type.
    
    Args:
        user_id: User ID
        request: Optional generation parameters
        db: Database session
        
    Returns:
        ExerciseResponse with generated exercise
        
    Raises:
        404: If user not found
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user's current skill profile
    profile = db.query(UserSkillProfile).filter(
        UserSkillProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User skill profile not found. Complete some sessions first."
        )
    
    # Get current difficulty (use requested or from profile)
    current_difficulty = request.difficulty if request else 5
    
    # Get adaptation recommendation
    adaptation_engine = AdaptationEngineFactory.create_default_engine()
    recommendation = adaptation_engine.get_recommendation(
        current_difficulty=current_difficulty,
        accuracy=profile.avg_accuracy,
        wpm=profile.avg_wpm,
        consistency_score=profile.consistency_score,
        error_rate=None,
    )
    
    # Generate exercise based on recommendation
    generator = ExerciseGenerator()
    weak_keys = profile.weak_keys or {}
    error_patterns = profile.error_patterns or {}
    
    if recommendation.exercise_type == "weak_key_drill":
        prompt = generator.generate_weak_key_drill(
            weak_keys=weak_keys,
            difficulty=recommendation.next_difficulty,
            duration_seconds=recommendation.suggested_duration_seconds,
        )
    elif recommendation.exercise_type == "error_pattern":
        prompt = generator.generate_error_pattern_exercise(
            error_patterns=error_patterns,
            weak_keys=weak_keys,
            difficulty=recommendation.next_difficulty,
            duration_seconds=recommendation.suggested_duration_seconds,
        )
    elif recommendation.exercise_type == "speed_challenge":
        prompt = generator.generate_speed_challenge(
            weak_keys=weak_keys,
            difficulty=recommendation.next_difficulty,
        )
    elif recommendation.exercise_type == "accuracy_focus":
        prompt = generator.generate_accuracy_focus(
            weak_keys=weak_keys,
            difficulty=recommendation.next_difficulty,
        )
    else:  # mixed
        prompt = generator.generate_mixed_exercise(
            weak_keys=weak_keys,
            error_patterns=error_patterns,
            difficulty=recommendation.next_difficulty,
            duration_seconds=recommendation.suggested_duration_seconds,
        )
    
    # Save exercise to database
    db_exercise = Exercise(
        user_id=user_id,
        text_prompt=prompt.text,
        exercise_type=prompt.type.value,
        difficulty=prompt.difficulty,
        focus_chars=prompt.focus_chars,
        description=prompt.description,
        expected_duration_seconds=prompt.expected_duration_seconds,
        exercise_metadata=prompt.metadata,
    )
    
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    
    return ExerciseResponse(
        exercise_id=db_exercise.id,
        text_prompt=db_exercise.text_prompt,
        exercise_type=db_exercise.exercise_type,
        difficulty=db_exercise.difficulty,
        focus_chars=db_exercise.focus_chars,
        description=db_exercise.description,
        expected_duration_seconds=db_exercise.expected_duration_seconds,
        adaptation_recommendation=AdaptationRecommendationResponse(
            next_difficulty=recommendation.next_difficulty,
            difficulty_change=recommendation.difficulty_change,
            exercise_type=recommendation.exercise_type,
            rationale=recommendation.rationale,
        ),
        generated_at=db_exercise.generated_at,
    )


@router.get(
    "/users/{user_id}/exercises/current",
    response_model=Optional[ExerciseResponse],
)
def get_current_exercise(
    user_id: int,
    db: Session = Depends(get_db),
) -> Optional[ExerciseResponse]:
    """
    Get the most recent unfinished exercise for user.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Current exercise or None if none available
    """
    exercise = db.query(Exercise).filter(
        Exercise.user_id == user_id,
        Exercise.is_active == True,
    ).order_by(Exercise.generated_at.desc()).first()
    
    if not exercise:
        return None
    
    return ExerciseResponse(
        exercise_id=exercise.id,
        text_prompt=exercise.text_prompt,
        exercise_type=exercise.exercise_type,
        difficulty=exercise.difficulty,
        focus_chars=exercise.focus_chars,
        description=exercise.description,
        expected_duration_seconds=exercise.expected_duration_seconds,
        adaptation_recommendation=None,
        generated_at=exercise.generated_at,
    )


@router.post(
    "/users/{user_id}/exercises/{exercise_id}/submit",
    response_model=ExerciseAttemptResponse,
)
def submit_exercise_attempt(
    user_id: int,
    exercise_id: int,
    attempt: ExerciseAttemptRequest,
    db: Session = Depends(get_db),
) -> ExerciseAttemptResponse:
    """
    Submit exercise attempt results.
    
    Records performance and triggers adaptation logic.
    
    Args:
        user_id: User ID
        exercise_id: Exercise ID
        attempt: Exercise attempt with results
        db: Database session
        
    Returns:
        ExerciseAttemptResponse with feedback and next recommendation
        
    Raises:
        404: If exercise not found
    """
    # Verify exercise exists and belongs to user
    exercise = db.query(Exercise).filter(
        Exercise.id == exercise_id,
        Exercise.user_id == user_id
    ).first()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    # Save attempt
    db_attempt = ExerciseAttempt(
        user_id=user_id,
        exercise_id=exercise_id,
        session_id=attempt.session_id,
        accuracy=attempt.accuracy,
        wpm=attempt.wpm,
        errors=attempt.errors,
        duration_seconds=attempt.duration_seconds,
        difficulty_felt=attempt.difficulty_felt,
        confidence_level=attempt.confidence_level,
        completed_at=datetime.utcnow(),
    )
    
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    
    # Mark exercise as attempted
    exercise.was_attempted = True
    exercise.attempt_count += 1
    exercise.is_active = False
    db.commit()
    
    # Process progress tracking (achievements, streaks, milestones)
    progress_result = {}
    if attempt.session_id:
        session = db.query(TypingSession).filter(
            TypingSession.id == attempt.session_id,
            TypingSession.user_id == user_id
        ).first()
        
        if session:
            tracker = ProgressTracker(db)
            progress_result = tracker.process_session_completion(user_id, session)
    
    # Get next recommendation
    profile = db.query(UserSkillProfile).filter(
        UserSkillProfile.user_id == user_id
    ).first()
    
    next_recommendation = None
    if profile:
        adaptation_engine = AdaptationEngineFactory.create_default_engine()
        rec = adaptation_engine.get_recommendation(
            current_difficulty=exercise.difficulty,
            accuracy=attempt.accuracy,
            wpm=attempt.wpm,
            consistency_score=profile.consistency_score,
        )
        next_recommendation = AdaptationRecommendationResponse(
            next_difficulty=rec.next_difficulty,
            difficulty_change=rec.difficulty_change,
            exercise_type=rec.exercise_type,
            rationale=rec.rationale,
        )
        db_attempt.adaptation_applied = rec.difficulty_change
    
    db.commit()
    
    return ExerciseAttemptResponse(
        attempt_id=db_attempt.id,
        exercise_id=exercise_id,
        accuracy=db_attempt.accuracy,
        wpm=db_attempt.wpm,
        errors=db_attempt.errors,
        duration_seconds=db_attempt.duration_seconds,
        was_successful=attempt.accuracy > 90,
        feedback=_generate_exercise_feedback(attempt.accuracy, exercise.difficulty),
        next_recommendation=next_recommendation,
    )


@router.get(
    "/exercises/placement-test",
    response_model=PlacementTestStartResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_placement_test(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db),
) -> PlacementTestStartResponse:
    """
    Start a placement test for user classification.
    
    Generates 3 difficulty levels (easy, medium, hard).
    User attempts all to establish starting level.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        PlacementTestStartResponse with test exercises
        
    Raises:
        404: If user not found
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate placement test
    service = PlacementTestService()
    exercises = service.generate_placement_test()
    
    # Save test record
    test = PlacementTest(
        user_id=user_id,
        test_duration_seconds=0,  # Will update on submit
    )
    
    db.add(test)
    db.commit()
    db.refresh(test)
    
    return PlacementTestStartResponse(
        test_id=test.id,
        user_id=user_id,
        instructions="Complete all three difficulty levels. This helps us find your starting point.",
        exercises=[
            {
                "level": "easy",
                "text": exercises[0].text,
                "description": exercises[0].description,
                "expected_duration_seconds": exercises[0].expected_duration_seconds,
            },
            {
                "level": "medium",
                "text": exercises[1].text,
                "description": exercises[1].description,
                "expected_duration_seconds": exercises[1].expected_duration_seconds,
            },
            {
                "level": "hard",
                "text": exercises[2].text,
                "description": exercises[2].description,
                "expected_duration_seconds": exercises[2].expected_duration_seconds,
            },
        ],
        created_at=test.created_at,
    )


@router.post(
    "/exercises/placement-test/{test_id}/submit",
    response_model=PlacementTestResultResponse,
)
def submit_placement_test(
    test_id: int,
    results: PlacementTestSubmitRequest,
    db: Session = Depends(get_db),
) -> PlacementTestResultResponse:
    """
    Submit placement test results.
    
    Evaluates performance and classifies user level.
    Sets recommended starting difficulty.
    
    Args:
        test_id: Placement test ID
        results: Test results (accuracy and WPM for each level)
        db: Database session
        
    Returns:
        PlacementTestResultResponse with classification and starting params
        
    Raises:
        404: If test not found
    """
    # Get test
    test = db.query(PlacementTest).filter(PlacementTest.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement test not found"
        )
    
    # Store results
    test.easy_accuracy = results.easy_accuracy
    test.easy_wpm = results.easy_wpm
    test.easy_duration = results.easy_duration
    
    test.medium_accuracy = results.medium_accuracy
    test.medium_wpm = results.medium_wpm
    test.medium_duration = results.medium_duration
    
    test.hard_accuracy = results.hard_accuracy
    test.hard_wpm = results.hard_wpm
    test.hard_duration = results.hard_duration
    
    test.completed_at = datetime.utcnow()
    
    # Evaluate
    service = PlacementTestService()
    result_list = [
        {"level": "easy", "accuracy": results.easy_accuracy, "wpm": results.easy_wpm},
        {"level": "medium", "accuracy": results.medium_accuracy, "wpm": results.medium_wpm},
        {"level": "hard", "accuracy": results.hard_accuracy, "wpm": results.hard_wpm},
    ]
    
    user_level, difficulty, confidence = service.evaluate_placement_test(result_list)
    
    test.classified_level = user_level.value
    test.recommended_difficulty = difficulty
    test.confidence = confidence
    
    db.commit()
    
    return PlacementTestResultResponse(
        test_id=test_id,
        classified_level=user_level.value,
        recommended_difficulty=difficulty,
        confidence=confidence,
        starting_exercise_type=PlacementTestService.get_starting_exercise_type(user_level),
        message=f"Welcome! We've classified you as {user_level.value}. Let's start at difficulty {difficulty}.",
    )


# Helper methods

def _generate_exercise_feedback(accuracy: float, difficulty: int) -> str:
    """
    Generate feedback for exercise attempt.
    
    Args:
        accuracy: User's accuracy on exercise
        difficulty: Exercise difficulty
        
    Returns:
        Feedback message
    """
    if accuracy >= 98:
        return "Perfect! You nailed it. Ready for something harder?"
    elif accuracy >= 95:
        return "Great work! You've got this."
    elif accuracy >= 90:
        return "Good effort. Keep practicing these weak keys."
    elif accuracy >= 85:
        return "You're getting there. Let's focus on accuracy for the next round."
    else:
        return "This is challenging—let's dial it back and build confidence."
