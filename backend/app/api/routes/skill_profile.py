"""
Skill Profile Routes

Endpoints for accessing and managing user skill profiles.
Provides insights into typing performance, weak keys, and personalized recommendations.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import UserSkillProfile, SkillSnapshot, WeakKeyProfile, UserSkillInsight, ErrorPatternProfile
from app.core.engine.skill_profile_service import SkillProfileService
from app.schemas.skill_profile import (
    UserSkillProfileResponse,
    SkillHistoryResponse,
    SkillHistoryPointResponse,
    SkillSummaryResponse,
    SkillComparisonResponse,
    SkillRecommendationResponse,
    ProfileUpdateResponse,
    SkillInsightResponse,
    WeakKeyStatsResponse,
    ErrorPatternResponse,
)

router = APIRouter(prefix="/api/v1/users", tags=["skill-profile"])


@router.get("/{user_id}/skill-profile", response_model=UserSkillProfileResponse)
def get_user_skill_profile(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserSkillProfileResponse:
    """
    Get complete user skill profile.
    
    Returns aggregated metrics, weak keys, error patterns, and achievements.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Complete skill profile
        
    Raises:
        404: If user not found or no profile yet
    """
    profile = db.query(UserSkillProfile).filter(
        UserSkillProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill profile not found. User may need more sessions."
        )
    
    return UserSkillProfileResponse(
        user_id=profile.user_id,
        avg_wpm=profile.avg_wpm,
        avg_accuracy=profile.avg_accuracy,
        total_sessions=profile.total_sessions,
        total_keystrokes=profile.total_keystrokes,
        total_errors=profile.total_errors,
        improvement_week=profile.improvement_week,
        improvement_month=profile.improvement_month,
        consistency_score=profile.consistency_score,
        weak_keys=profile.weak_keys,
        error_patterns=profile.error_patterns,
        best_wpm=profile.best_wpm,
        best_accuracy=profile.best_accuracy,
        longest_streak=profile.longest_streak,
        current_streak=profile.current_streak,
        last_updated=profile.last_updated,
    )


@router.get("/{user_id}/skill-history", response_model=SkillHistoryResponse)
def get_skill_history(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> SkillHistoryResponse:
    """
    Get skill progression history over time.
    
    Returns snapshots of skill metrics over specified period.
    Enables "where was I 2 weeks ago vs now" insights.
    
    Args:
        user_id: User ID
        days: Number of days to look back (1-365)
        db: Database session
        
    Returns:
        Skill history with trend analysis
        
    Raises:
        404: If user not found
    """
    # Verify user exists
    profile = db.query(UserSkillProfile).filter(
        UserSkillProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User skill profile not found"
        )
    
    since = datetime.utcnow() - timedelta(days=days)
    
    snapshots = db.query(SkillSnapshot).filter(
        SkillSnapshot.user_id == user_id,
        SkillSnapshot.snapshot_date >= since
    ).order_by(SkillSnapshot.snapshot_date).all()
    
    history = [
        SkillHistoryPointResponse(
            session_id=s.session_id or 0,
            wpm=s.wpm,
            accuracy=s.accuracy,
            total_sessions=s.total_sessions,
            cumulative_wpm_avg=s.cumulative_wpm_avg,
            cumulative_accuracy_avg=s.cumulative_accuracy_avg,
            wpm_change=s.wpm_change,
            accuracy_change=s.accuracy_change,
            snapshot_date=s.snapshot_date,
        )
        for s in snapshots
    ]
    
    # Determine trend
    trend = "stable"
    if len(history) >= 2:
        first_wpm = history[0].cumulative_wpm_avg
        last_wpm = history[-1].cumulative_wpm_avg
        change = last_wpm - first_wpm
        
        if change > first_wpm * 0.05:  # More than 5% improvement
            trend = "improving"
        elif change < first_wpm * -0.05:  # More than 5% decline
            trend = "declining"
    
    # Calculate momentum (recent change)
    momentum = 0.0
    if len(history) >= 2:
        recent_window = len(history) // 3 or 1
        recent_avg = sum(p.wpm_change or 0 for p in history[-recent_window:]) / recent_window
        momentum = recent_avg
    
    return SkillHistoryResponse(
        user_id=user_id,
        period_days=days,
        history=history,
        overall_trend=trend,
        current_momentum=momentum,
    )


@router.get("/{user_id}/skill-summary", response_model=SkillSummaryResponse)
def get_skill_summary(
    user_id: int,
    db: Session = Depends(get_db),
) -> SkillSummaryResponse:
    """
    Get quick skill summary for dashboard.
    
    Condensed view with key metrics and latest insight.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Skill summary
        
    Raises:
        404: If user not found
    """
    profile = db.query(UserSkillProfile).filter(
        UserSkillProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User skill profile not found"
        )
    
    # Determine status
    if profile.avg_wpm < 30:
        status_str = "beginner"
    elif profile.avg_wpm < 60:
        status_str = "intermediate"
    else:
        status_str = "advanced"
    
    # Confidence based on total sessions
    confidence = min(profile.total_sessions / 20, 1.0)
    
    # Get top insight
    top_insight = db.query(UserSkillInsight).filter(
        UserSkillInsight.user_id == user_id,
        UserSkillInsight.is_active == True
    ).order_by(UserSkillInsight.priority.desc()).first()
    
    top_insight_response = None
    if top_insight:
        top_insight_response = SkillInsightResponse(
            insight_type=top_insight.insight_type,
            title=top_insight.title,
            description=top_insight.description,
            metric_name=top_insight.metric_name,
            metric_value=top_insight.metric_value,
            recommendation=top_insight.recommendation,
            tone=top_insight.tone,
            priority=top_insight.priority,
        )
    
    # Get weakest key
    weak_key = None
    if profile.weak_keys:
        weak_key = list(profile.weak_keys.keys())[0]
    
    # Achievement level (0-1)
    achievement = min(profile.total_sessions / 50, 1.0)
    
    return SkillSummaryResponse(
        user_id=user_id,
        avg_wpm=profile.avg_wpm,
        avg_accuracy=profile.avg_accuracy,
        total_sessions=profile.total_sessions,
        status=status_str,
        confidence_level=confidence,
        top_insight=top_insight_response,
        weak_key=weak_key,
        milestone=None,  # TODO: Determine latest milestone
        achievement_level=achievement,
    )


@router.get("/{user_id}/weak-keys-detail", response_model=List[WeakKeyStatsResponse])
def get_weak_keys_detail(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> List[WeakKeyStatsResponse]:
    """
    Get detailed weak key profiles.
    
    Returns characters with highest error rates, sorted by error rate.
    
    Args:
        user_id: User ID
        limit: Max keys to return
        db: Database session
        
    Returns:
        List of weak key stats
    """
    weak_keys = db.query(WeakKeyProfile).filter(
        WeakKeyProfile.user_id == user_id
    ).order_by(WeakKeyProfile.error_rate.desc()).limit(limit).all()
    
    return [
        WeakKeyStatsResponse(
            character=wk.character,
            total_attempts=wk.total_attempts,
            total_errors=wk.total_errors,
            error_rate=wk.error_rate,
            error_distribution=wk.error_distribution,
            recent_error_rate=wk.recent_error_rate,
            trend=wk.trend,
            improvement_pct=wk.improvement_pct,
        )
        for wk in weak_keys
    ]


@router.get("/{user_id}/error-patterns", response_model=List[ErrorPatternResponse])
def get_error_patterns(
    user_id: int,
    db: Session = Depends(get_db),
) -> List[ErrorPatternResponse]:
    """
    Get detailed error patterns.
    
    Returns breakdown of error types and specific patterns.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        List of error patterns
    """
    error_patterns = db.query(ErrorPatternProfile).filter(
        ErrorPatternProfile.user_id == user_id
    ).order_by(ErrorPatternProfile.total_occurrences.desc()).all()
    
    return [
        ErrorPatternResponse(
            error_type=ep.error_type,
            total_occurrences=ep.total_occurrences,
            percentage=ep.percentage,
            pattern_details=ep.pattern_details,
            under_pressure=ep.appears_under_pressure,
            when_tired=ep.appears_when_tired,
            sessions_with_error=ep.sessions_with_error,
        )
        for ep in error_patterns
    ]


@router.get("/{user_id}/insights", response_model=List[SkillInsightResponse])
def get_active_insights(
    user_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
) -> List[SkillInsightResponse]:
    """
    Get active coaching insights.
    
    Returns personalized, non-judgmental insights prioritized by relevance.
    
    Args:
        user_id: User ID
        limit: Max insights to return
        db: Database session
        
    Returns:
        List of active insights
    """
    insights = db.query(UserSkillInsight).filter(
        UserSkillInsight.user_id == user_id,
        UserSkillInsight.is_active == True
    ).order_by(UserSkillInsight.priority.desc()).limit(limit).all()
    
    return [
        SkillInsightResponse(
            insight_type=i.insight_type,
            title=i.title,
            description=i.description,
            metric_name=i.metric_name,
            metric_value=i.metric_value,
            recommendation=i.recommendation,
            tone=i.tone,
            priority=i.priority,
        )
        for i in insights
    ]


@router.get("/{user_id}/recommendations", response_model=SkillRecommendationResponse)
def get_recommendations(
    user_id: int,
    current_difficulty: int = Query(1, ge=1, le=10),
    db: Session = Depends(get_db),
) -> SkillRecommendationResponse:
    """
    Get personalized recommendations.
    
    Suggests difficulty adjustments, practice focus areas, and encouragement.
    
    Args:
        user_id: User ID
        current_difficulty: Current difficulty level
        db: Database session
        
    Returns:
        Personalized recommendations
    """
    profile = db.query(UserSkillProfile).filter(
        UserSkillProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User skill profile not found"
        )
    
    # Recommend difficulty based on accuracy
    recommended_difficulty = current_difficulty
    reason = "Maintaining current difficulty"
    
    if profile.avg_accuracy > 97:
        recommended_difficulty = min(current_difficulty + 1, 10)
        reason = "Your accuracy is excellent - try a harder difficulty"
    elif profile.avg_accuracy < 90:
        recommended_difficulty = max(current_difficulty - 1, 1)
        reason = "Let's build solid accuracy first"
    
    # Focus areas (weak keys)
    focus_areas = list(profile.weak_keys.keys())[:3]
    
    return SkillRecommendationResponse(
        user_id=user_id,
        recommended_difficulty=recommended_difficulty,
        current_difficulty=current_difficulty,
        reason=reason,
        focus_areas=focus_areas,
        practice_method="drill",
        observations=[
            f"You've completed {profile.total_sessions} sessions",
            f"Your best WPM is {profile.best_wpm or 0:.0f}",
        ],
        strengths=[],
        growth_areas=focus_areas,
        motivational_message="Every keystroke is progress. You're building real skill.",
    )


@router.post("/{user_id}/profile/update-session")
def trigger_profile_update_for_session(
    user_id: int,
    session_id: int,
    db: Session = Depends(get_db),
) -> ProfileUpdateResponse:
    """
    Manually trigger skill profile update for a session.
    
    Called after session keystroke batch submission.
    
    Args:
        user_id: User ID
        session_id: Session ID
        db: Database session
        
    Returns:
        Profile update response
    """
    service = SkillProfileService(db)
    
    # Update profile
    updated_profile = service.update_skill_profile_for_session(user_id, session_id)
    
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not update skill profile"
        )
    
    # Get new insights
    insights = db.query(UserSkillInsight).filter(
        UserSkillInsight.user_id == user_id,
        UserSkillInsight.last_seen >= datetime.utcnow() - timedelta(minutes=1)
    ).all()
    
    return ProfileUpdateResponse(
        user_id=user_id,
        session_id=session_id,
        profile_updated=True,
        metrics_changed={
            'avg_wpm': updated_profile.avg_wpm,
            'avg_accuracy': updated_profile.avg_accuracy,
            'total_sessions': updated_profile.total_sessions,
        },
        new_insights=[
            SkillInsightResponse(
                insight_type=i.insight_type,
                title=i.title,
                description=i.description,
                metric_name=i.metric_name,
                metric_value=i.metric_value,
                recommendation=i.recommendation,
                tone=i.tone,
                priority=i.priority,
            )
            for i in insights[:3]
        ],
        updated_weak_keys=list(updated_profile.weak_keys.keys())[:5],
        profile_version=updated_profile.profile_version,
        last_updated=updated_profile.last_updated,
        next_update_estimated=datetime.utcnow() + timedelta(hours=1),
    )
