"""
Progress and Gamification API Endpoints

Exposes achievements, streaks, milestones, and progress visualization data.
"""

from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import (
    User,
    Achievement,
    UserStreak,
    Milestone,
    ProgressSnapshot,
    TypingSession,
    UserSkillProfile,
)
from app.services.progress_tracker import ProgressTracker
from app.schemas.progress import (
    ProgressStatsResponse,
    AchievementResponse,
    StreakResponse,
    MilestoneResponse,
    KeyboardHeatmapResponse,
    TrendDataResponse,
)

router = APIRouter(prefix="/api/v1", tags=["progress"])


@router.get("/users/{user_id}/progress/stats", response_model=ProgressStatsResponse)
def get_progress_stats(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get comprehensive progress statistics for a user.
    
    Includes:
    - Overall skill metrics (WPM, accuracy, consistency)
    - Achievements earned
    - Current streaks and personal bests
    - Recent milestones
    - Trend data (week/month improvement)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tracker = ProgressTracker(db)
    stats = tracker.get_user_progress_stats(user_id)

    if not stats:
        raise HTTPException(status_code=404, detail="No progress data found")

    return stats


@router.get("/users/{user_id}/achievements", response_model=list[AchievementResponse])
def get_user_achievements(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get all achievements earned by user.
    
    Returns achievements grouped by rarity with earn dates.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    achievements = (
        db.query(Achievement)
        .filter(Achievement.user_id == user_id)
        .order_by(Achievement.earned_at.desc())
        .all()
    )

    return [
        AchievementResponse(
            type=a.achievement_type,
            title=a.title,
            description=a.description,
            rarity=a.rarity,
            icon=a.icon,
            earned_at=a.earned_at,
        )
        for a in achievements
    ]


@router.get("/users/{user_id}/streaks", response_model=list[StreakResponse])
def get_user_streaks(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get user's practice streaks.
    
    Includes:
    - Daily practice streak (consecutive days)
    - Error-free session streak
    - Personal bests for each streak type
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    streaks = (
        db.query(UserStreak)
        .filter(UserStreak.user_id == user_id)
        .all()
    )

    return [
        StreakResponse(
            type=s.streak_type,
            current_count=s.current_count,
            longest_count=s.longest_count,
            last_activity_date=s.last_activity_date,
        )
        for s in streaks
    ]


@router.get("/users/{user_id}/milestones", response_model=list[MilestoneResponse])
def get_user_milestones(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Get user's recent milestones.
    
    Milestones mark significant achievements like:
    - First 50 WPM
    - Personal records
    - Error-free sessions
    - Consistency breakthroughs
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    milestones = (
        db.query(Milestone)
        .filter(Milestone.user_id == user_id)
        .order_by(Milestone.achieved_at.desc())
        .limit(limit)
        .all()
    )

    return [
        MilestoneResponse(
            type=m.milestone_type,
            title=m.title,
            description=m.description,
            metric_name=m.metric_name,
            metric_value=m.metric_value,
            achieved_at=m.achieved_at,
            celebration_shown=m.celebration_shown,
        )
        for m in milestones
    ]


@router.get("/users/{user_id}/progress/trend", response_model=list[TrendDataResponse])
def get_progress_trend(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """
    Get progress trend data for visualization.
    
    Returns daily snapshots showing:
    - WPM progression
    - Accuracy progression
    - Weekly/monthly improvement %
    - Session count
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    start_date = datetime.utcnow() - timedelta(days=days)

    snapshots = (
        db.query(ProgressSnapshot)
        .filter(
            ProgressSnapshot.user_id == user_id,
            ProgressSnapshot.snapshot_date >= start_date,
        )
        .order_by(ProgressSnapshot.snapshot_date.asc())
        .all()
    )

    return [
        TrendDataResponse(
            date=s.snapshot_date,
            avg_wpm=s.avg_wpm,
            avg_accuracy=s.avg_accuracy,
            best_wpm=s.best_wpm,
            best_accuracy=s.best_accuracy,
            total_sessions=s.total_sessions,
            week_improvement=s.week_improvement_pct,
            month_improvement=s.month_improvement_pct,
        )
        for s in snapshots
    ]


@router.get("/users/{user_id}/keyboard-heatmap", response_model=KeyboardHeatmapResponse)
def get_keyboard_heatmap(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get keyboard heatmap data for visualization.
    
    Shows error rates per character:
    - Green: Low error rate (< 5%)
    - Yellow: Moderate (5-15%)
    - Red: High (> 15%)
    
    Visual representation of weak spots on keyboard.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tracker = ProgressTracker(db)
    heatmap = tracker.get_keyboard_heatmap(user_id)

    # Convert to color-coded format for visualization
    color_heatmap = {}
    for char, error_rate in heatmap.items():
        if error_rate < 0.05:
            color = "green"
        elif error_rate < 0.15:
            color = "yellow"
        else:
            color = "red"

        color_heatmap[char] = {
            "error_rate": error_rate,
            "color": color,
        }

    return KeyboardHeatmapResponse(
        heatmap=color_heatmap,
        generated_at=datetime.utcnow(),
    )


@router.get("/users/{user_id}/stats/live")
def get_live_stats(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get live session statistics.
    
    Returns real-time metrics for the current or most recent session:
    - Current WPM
    - Current accuracy
    - Errors so far
    - Time elapsed
    - Progress toward session goals
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get most recent session
    session = (
        db.query(TypingSession)
        .filter(TypingSession.user_id == user_id)
        .order_by(TypingSession.started_at.desc())
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="No sessions found")

    return {
        "session_id": session.id,
        "wpm": session.wpm,
        "accuracy": session.accuracy,
        "errors": session.errors,
        "duration_seconds": session.duration_seconds,
        "key_presses": session.key_presses,
        "status": session.status,
        "started_at": session.started_at,
    }


@router.post("/users/{user_id}/milestones/{milestone_id}/celebrate")
def celebrate_milestone(
    user_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
):
    """
    Mark a milestone celebration as shown.
    
    Used to track which celebrations have been displayed to user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    milestone = (
        db.query(Milestone)
        .filter(
            Milestone.id == milestone_id,
            Milestone.user_id == user_id,
        )
        .first()
    )

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    milestone.celebration_shown = True
    db.commit()

    return {
        "success": True,
        "message": "Celebration marked as shown",
    }


@router.get("/users/{user_id}/dashboard/summary")
def get_dashboard_summary(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get concise summary for dashboard widget.
    
    Quick overview including:
    - Current stats
    - Recent achievements
    - Active streaks
    - Next goals
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skill_profile = (
        db.query(UserSkillProfile)
        .filter(UserSkillProfile.user_id == user_id)
        .first()
    )

    # Recent achievements
    recent_achievements = (
        db.query(Achievement)
        .filter(Achievement.user_id == user_id)
        .order_by(Achievement.earned_at.desc())
        .limit(3)
        .all()
    )

    # Active streaks
    active_streaks = (
        db.query(UserStreak)
        .filter(UserStreak.user_id == user_id)
        .all()
    )

    # Next milestone targets
    next_targets = []
    if skill_profile:
        if (skill_profile.best_wpm or 0) < 50:
            next_targets.append("Reach 50 WPM")
        if (skill_profile.best_accuracy or 0) < 95:
            next_targets.append("Achieve 95% accuracy")
        if skill_profile.consistency_score < 85:
            next_targets.append("Build consistency")

    return {
        "current_stats": {
            "avg_wpm": skill_profile.avg_wpm if skill_profile else 0,
            "avg_accuracy": skill_profile.avg_accuracy if skill_profile else 0,
            "consistency_score": skill_profile.consistency_score if skill_profile else 0,
            "total_sessions": skill_profile.total_sessions if skill_profile else 0,
        },
        "recent_achievements": [
            {
                "title": a.title,
                "rarity": a.rarity,
                "earned_at": a.earned_at.isoformat(),
            }
            for a in recent_achievements
        ],
        "active_streaks": [
            {
                "type": s.streak_type,
                "count": s.current_count,
            }
            for s in active_streaks
        ],
        "next_targets": next_targets,
    }
