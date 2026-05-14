"""
Progress Tracking Service

Manages achievements, streaks, milestones, and progress visualization.
Creates the "I'm actually getting better" feeling through comprehensive feedback.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from sqlalchemy.orm import Session

from app.db.models import (
    User,
    TypingSession,
    UserSkillProfile,
    Achievement,
    UserStreak,
    Milestone,
    ProgressSnapshot,
    Exercise,
    ExerciseAttempt,
)


class ProgressTracker:
    """
    Comprehensive progress tracking and gamification engine.
    
    Responsible for:
    - Detecting and awarding achievements
    - Maintaining practice streaks
    - Recording meaningful milestones
    - Generating progress snapshots for visualization
    - Creating motivational feedback
    """

    def __init__(self, db: Session):
        self.db = db

    def process_session_completion(self, user_id: int, session: TypingSession) -> Dict:
        """
        Called when a typing session completes.
        Triggers achievement detection, milestone checking, and progress updates.
        
        Returns:
            Dict with new achievements, milestones, and feedback
        """
        result = {
            "new_achievements": [],
            "new_milestones": [],
            "streak_updates": {},
            "motivational_message": "",
            "progress_snapshot_created": False,
        }

        # Get user's skill profile
        skill_profile = (
            self.db.query(UserSkillProfile)
            .filter(UserSkillProfile.user_id == user_id)
            .first()
        )

        if not skill_profile:
            return result

        # Check for achievements
        result["new_achievements"] = self._check_achievements(
            user_id, session, skill_profile
        )

        # Check for milestones
        result["new_milestones"] = self._check_milestones(
            user_id, session, skill_profile
        )

        # Update streaks
        result["streak_updates"] = self._update_streaks(user_id, session)

        # Create progress snapshot (daily)
        snapshot_created = self._create_daily_snapshot(user_id, skill_profile)
        result["progress_snapshot_created"] = snapshot_created

        # Generate motivational message
        result["motivational_message"] = self._generate_motivational_message(
            user_id, session, skill_profile, result
        )

        return result

    def _check_achievements(
        self, user_id: int, session: TypingSession, skill_profile: UserSkillProfile
    ) -> List[Dict]:
        """Check and award new achievements."""
        new_achievements = []

        # Achievement definitions
        achievements_to_check = [
            # Speed achievements
            {
                "type": "speed_10_wpm",
                "condition": lambda s, sp: (s.wpm or 0) >= 10,
                "title": "Getting Started",
                "description": "Reached 10 WPM",
                "rarity": "common",
            },
            {
                "type": "speed_25_wpm",
                "condition": lambda s, sp: (s.wpm or 0) >= 25,
                "title": "Steady Typist",
                "description": "Reached 25 WPM",
                "rarity": "common",
            },
            {
                "type": "speed_50_wpm",
                "condition": lambda s, sp: (s.wpm or 0) >= 50,
                "title": "Speed Runner",
                "description": "Reached 50 WPM!",
                "rarity": "rare",
            },
            {
                "type": "speed_75_wpm",
                "condition": lambda s, sp: (s.wpm or 0) >= 75,
                "title": "Velocity Demon",
                "description": "Reached 75 WPM!",
                "rarity": "rare",
            },
            {
                "type": "speed_100_wpm",
                "condition": lambda s, sp: (s.wpm or 0) >= 100,
                "title": "Lightning Fast",
                "description": "Reached 100 WPM!",
                "rarity": "epic",
            },
            # Accuracy achievements
            {
                "type": "accuracy_95",
                "condition": lambda s, sp: (s.accuracy or 0) >= 95,
                "title": "Precision Expert",
                "description": "Achieved 95% accuracy",
                "rarity": "rare",
            },
            {
                "type": "accuracy_98",
                "condition": lambda s, sp: (s.accuracy or 0) >= 98,
                "title": "Perfect Typist",
                "description": "Achieved 98% accuracy",
                "rarity": "epic",
            },
            {
                "type": "perfect_session",
                "condition": lambda s, sp: (s.accuracy or 0) >= 100 and s.errors == 0,
                "title": "Flawless Victory",
                "description": "Completed a session with zero errors",
                "rarity": "legendary",
            },
            # Consistency achievements
            {
                "type": "consistency_master",
                "condition": lambda s, sp: sp.consistency_score >= 85,
                "title": "Consistency Master",
                "description": "Maintained 85+ consistency score",
                "rarity": "rare",
            },
            # Volume achievements
            {
                "type": "milestone_10_sessions",
                "condition": lambda s, sp: sp.total_sessions >= 10,
                "title": "Dedicated Learner",
                "description": "Completed 10 typing sessions",
                "rarity": "common",
            },
            {
                "type": "milestone_50_sessions",
                "condition": lambda s, sp: sp.total_sessions >= 50,
                "title": "Devoted Typist",
                "description": "Completed 50 typing sessions",
                "rarity": "rare",
            },
            {
                "type": "milestone_100_sessions",
                "condition": lambda s, sp: sp.total_sessions >= 100,
                "title": "Typing Legend",
                "description": "Completed 100 typing sessions",
                "rarity": "epic",
            },
            # Personal improvement
            {
                "type": "improvement_50_percent",
                "condition": lambda s, sp: (
                    sp.improvement_month is not None and sp.improvement_month >= 50
                ),
                "title": "Rapid Improvement",
                "description": "Improved 50% over the last month",
                "rarity": "epic",
            },
        ]

        # Check each achievement
        for achievement_def in achievements_to_check:
            if achievement_def["condition"](session, skill_profile):
                # Check if already earned
                existing = (
                    self.db.query(Achievement)
                    .filter(
                        Achievement.user_id == user_id,
                        Achievement.achievement_type == achievement_def["type"],
                    )
                    .first()
                )

                if not existing:
                    # Award new achievement
                    new_achievement = Achievement(
                        user_id=user_id,
                        achievement_type=achievement_def["type"],
                        title=achievement_def["title"],
                        description=achievement_def["description"],
                        rarity=achievement_def["rarity"],
                        progress_value=session.wpm
                        if "speed" in achievement_def["type"]
                        else session.accuracy,
                        requirement=achievement_def["description"],
                    )
                    self.db.add(new_achievement)
                    self.db.flush()

                    new_achievements.append(
                        {
                            "type": achievement_def["type"],
                            "title": achievement_def["title"],
                            "rarity": achievement_def["rarity"],
                            "message": f"🎉 Unlocked: {achievement_def['title']}!",
                        }
                    )

        if new_achievements:
            self.db.commit()

        return new_achievements

    def _check_milestones(
        self, user_id: int, session: TypingSession, skill_profile: UserSkillProfile
    ) -> List[Dict]:
        """Check and record meaningful milestones."""
        milestones = []

        # Milestone definitions
        milestone_checks = [
            {
                "type": "first_50_wpm",
                "condition": lambda s, sp: (s.wpm or 0) >= 50,
                "title": "First 50 WPM! 🚀",
                "description": f"Congrats! You just hit 50 WPM. That's real progress!",
                "metric_name": "wpm",
            },
            {
                "type": "first_95_accuracy",
                "condition": lambda s, sp: (s.accuracy or 0) >= 95,
                "title": "95% Accuracy Reached! 🎯",
                "description": "You're incredibly precise. Keep it up!",
                "metric_name": "accuracy",
            },
            {
                "type": "best_wpm_personal_record",
                "condition": lambda s, sp: (s.wpm or 0) > (sp.best_wpm or 0),
                "title": "New Personal Record! ⚡",
                "description": f"You just beat your best speed! New record: {s.wpm:.1f} WPM",
                "metric_name": "wpm",
            },
            {
                "type": "best_accuracy_personal_record",
                "condition": lambda s, sp: (s.accuracy or 0) > (sp.best_accuracy or 0),
                "title": "Accuracy Record! 🎯",
                "description": f"Your best accuracy ever: {s.accuracy:.1f}%",
                "metric_name": "accuracy",
            },
            {
                "type": "error_free_session",
                "condition": lambda s, sp: s.errors == 0,
                "title": "Flawless! 🌟",
                "description": "You completed a session with zero errors. Amazing!",
                "metric_name": "errors",
            },
            {
                "type": "consistency_breakthrough",
                "condition": lambda s, sp: sp.consistency_score >= 85,
                "title": "Consistency Breakthrough! 📈",
                "description": "Your performance is now very consistent. You know your ability!",
                "metric_name": "consistency",
            },
        ]

        for milestone_def in milestone_checks:
            if milestone_def["condition"](session, skill_profile):
                # Check if already recorded
                existing = (
                    self.db.query(Milestone)
                    .filter(
                        Milestone.user_id == user_id,
                        Milestone.milestone_type == milestone_def["type"],
                    )
                    .first()
                )

                if not existing:
                    # Record milestone
                    metric_value = (
                        session.wpm
                        if milestone_def["metric_name"] == "wpm"
                        else (
                            session.accuracy
                            if milestone_def["metric_name"] == "accuracy"
                            else 0
                        )
                    )

                    new_milestone = Milestone(
                        user_id=user_id,
                        milestone_type=milestone_def["type"],
                        title=milestone_def["title"],
                        description=milestone_def["description"],
                        metric_name=milestone_def["metric_name"],
                        metric_value=metric_value,
                        session_id=session.id,
                    )
                    self.db.add(new_milestone)
                    self.db.flush()

                    milestones.append(
                        {
                            "type": milestone_def["type"],
                            "title": milestone_def["title"],
                            "message": milestone_def["description"],
                        }
                    )

        if milestones:
            self.db.commit()

        return milestones

    def _update_streaks(self, user_id: int, session: TypingSession) -> Dict:
        """Update practice streaks."""
        updates = {}

        # Daily practice streak
        daily_streak = (
            self.db.query(UserStreak)
            .filter(
                UserStreak.user_id == user_id,
                UserStreak.streak_type == "days_practiced",
            )
            .first()
        )

        today = datetime.utcnow().date()

        if not daily_streak:
            daily_streak = UserStreak(
                user_id=user_id,
                streak_type="days_practiced",
                current_count=1,
                longest_count=1,
                last_activity_date=datetime.utcnow(),
            )
            self.db.add(daily_streak)
        else:
            last_activity = daily_streak.last_activity_date.date()
            yesterday = today - timedelta(days=1)

            if last_activity == today:
                # Already practiced today, don't increment
                pass
            elif last_activity == yesterday:
                # Streak continues
                daily_streak.current_count += 1
                daily_streak.longest_count = max(
                    daily_streak.longest_count, daily_streak.current_count
                )
                daily_streak.last_activity_date = datetime.utcnow()
            else:
                # Streak broken, start new one
                daily_streak.current_count = 1
                daily_streak.started_at = datetime.utcnow()
                daily_streak.last_activity_date = datetime.utcnow()

        updates["daily_streak"] = {
            "current": daily_streak.current_count,
            "personal_best": daily_streak.longest_count,
        }

        # Error-free session streak
        if session.errors == 0:
            error_free_streak = (
                self.db.query(UserStreak)
                .filter(
                    UserStreak.user_id == user_id,
                    UserStreak.streak_type == "error_free_sessions",
                )
                .first()
            )

            if not error_free_streak:
                error_free_streak = UserStreak(
                    user_id=user_id,
                    streak_type="error_free_sessions",
                    current_count=1,
                    longest_count=1,
                    last_activity_date=datetime.utcnow(),
                )
                self.db.add(error_free_streak)
            else:
                error_free_streak.current_count += 1
                error_free_streak.longest_count = max(
                    error_free_streak.longest_count, error_free_streak.current_count
                )

            updates["error_free_streak"] = {
                "current": error_free_streak.current_count,
                "personal_best": error_free_streak.longest_count,
            }

        self.db.commit()
        return updates

    def _create_daily_snapshot(
        self, user_id: int, skill_profile: UserSkillProfile
    ) -> bool:
        """Create a daily progress snapshot for visualization."""
        today = datetime.utcnow().date()

        # Check if already created today
        existing_snapshot = (
            self.db.query(ProgressSnapshot)
            .filter(
                ProgressSnapshot.user_id == user_id,
                ProgressSnapshot.snapshot_date >= datetime.combine(
                    today, datetime.min.time()
                ),
            )
            .first()
        )

        if existing_snapshot:
            return False

        # Calculate keyboard heatmap
        keyboard_heatmap = {}
        for char, data in skill_profile.weak_keys.items():
            if isinstance(data, dict):
                keyboard_heatmap[char] = data.get("error_rate", 0)

        # Get top 5 weak keys
        weak_keys_sorted = sorted(
            skill_profile.weak_keys.items(),
            key=lambda x: x[1].get("error_rate", 0) if isinstance(x[1], dict) else 0,
            reverse=True,
        )
        weak_keys_at_time = [char for char, _ in weak_keys_sorted[:5]]

        # Calculate week/month improvement
        week_ago = datetime.utcnow() - timedelta(days=7)
        month_ago = datetime.utcnow() - timedelta(days=30)

        week_snapshots = (
            self.db.query(ProgressSnapshot)
            .filter(
                ProgressSnapshot.user_id == user_id,
                ProgressSnapshot.snapshot_date >= week_ago,
            )
            .order_by(ProgressSnapshot.snapshot_date.desc())
            .all()
        )

        week_improvement = None
        if len(week_snapshots) >= 2:
            oldest = week_snapshots[-1]
            newest = week_snapshots[0]
            if oldest.avg_wpm and newest.avg_wpm:
                week_improvement = (
                    ((newest.avg_wpm - oldest.avg_wpm) / oldest.avg_wpm) * 100
                )

        month_snapshots = (
            self.db.query(ProgressSnapshot)
            .filter(
                ProgressSnapshot.user_id == user_id,
                ProgressSnapshot.snapshot_date >= month_ago,
            )
            .order_by(ProgressSnapshot.snapshot_date.desc())
            .all()
        )

        month_improvement = None
        if len(month_snapshots) >= 2:
            oldest = month_snapshots[-1]
            newest = month_snapshots[0]
            if oldest.avg_wpm and newest.avg_wpm:
                month_improvement = (
                    ((newest.avg_wpm - oldest.avg_wpm) / oldest.avg_wpm) * 100
                )

        # Create snapshot
        snapshot = ProgressSnapshot(
            user_id=user_id,
            avg_wpm=skill_profile.avg_wpm,
            avg_accuracy=skill_profile.avg_accuracy,
            best_wpm=skill_profile.best_wpm,
            best_accuracy=skill_profile.best_accuracy,
            total_sessions=skill_profile.total_sessions,
            total_practice_minutes=skill_profile.total_sessions * 2,  # Approximate
            total_keystrokes=skill_profile.total_keystrokes,
            total_errors=skill_profile.total_errors,
            keyboard_heatmap=keyboard_heatmap,
            weak_keys_at_time=weak_keys_at_time,
            week_improvement_pct=week_improvement,
            month_improvement_pct=month_improvement,
        )

        self.db.add(snapshot)
        self.db.commit()

        return True

    def _generate_motivational_message(
        self,
        user_id: int,
        session: TypingSession,
        skill_profile: UserSkillProfile,
        progress_result: Dict,
    ) -> str:
        """Generate personalized motivational message."""
        messages = []

        # Celebrate milestones
        if progress_result["new_milestones"]:
            messages.append(progress_result["new_milestones"][0]["title"])

        # Celebrate achievements
        if progress_result["new_achievements"]:
            messages.append(
                f"Unlocked: {progress_result['new_achievements'][0]['title']}"
            )

        # Streak bonus
        if progress_result["streak_updates"]:
            daily_streak = progress_result["streak_updates"].get("daily_streak", {})
            if daily_streak.get("current", 0) >= 3:
                messages.append(
                    f"🔥 {daily_streak['current']}-day streak! Keep it going!"
                )

        # Performance-based messages
        if session.accuracy and session.accuracy >= 98:
            messages.append("Your precision is outstanding! 🎯")
        elif session.accuracy and session.accuracy >= 95:
            messages.append("Excellent accuracy! You're in the zone. 💪")

        if session.wpm and session.wpm >= skill_profile.best_wpm:
            messages.append("You beat your personal record! 🚀")

        # Improvement notice
        if (
            skill_profile.improvement_week
            and skill_profile.improvement_week > 10
        ):
            messages.append(
                f"You've improved {skill_profile.improvement_week:.1f}% this week! 📈"
            )

        # Generic encouragement if nothing else
        if not messages:
            encouragements = [
                "Great session! Every keystroke makes you better. 💪",
                "You're on the path to mastery. Keep practicing! 🎯",
                "Your consistency is paying off. Well done! ✨",
                "The more you practice, the better you get. Keep it up! 🌟",
            ]
            import random

            messages.append(random.choice(encouragements))

        return " ".join(messages)

    def get_user_progress_stats(self, user_id: int) -> Dict:
        """Get comprehensive progress stats for dashboard."""
        skill_profile = (
            self.db.query(UserSkillProfile)
            .filter(UserSkillProfile.user_id == user_id)
            .first()
        )

        if not skill_profile:
            return {}

        # Get achievements
        achievements = (
            self.db.query(Achievement)
            .filter(Achievement.user_id == user_id)
            .all()
        )

        # Get streaks
        streaks = (
            self.db.query(UserStreak)
            .filter(UserStreak.user_id == user_id)
            .all()
        )

        # Get recent milestones
        recent_milestones = (
            self.db.query(Milestone)
            .filter(Milestone.user_id == user_id)
            .order_by(Milestone.achieved_at.desc())
            .limit(5)
            .all()
        )

        # Get recent progress snapshots
        snapshots = (
            self.db.query(ProgressSnapshot)
            .filter(ProgressSnapshot.user_id == user_id)
            .order_by(ProgressSnapshot.snapshot_date.desc())
            .limit(30)
            .all()
        )

        return {
            "skill_profile": {
                "avg_wpm": skill_profile.avg_wpm,
                "avg_accuracy": skill_profile.avg_accuracy,
                "best_wpm": skill_profile.best_wpm,
                "best_accuracy": skill_profile.best_accuracy,
                "consistency_score": skill_profile.consistency_score,
                "total_sessions": skill_profile.total_sessions,
                "total_keystrokes": skill_profile.total_keystrokes,
                "improvement_week": skill_profile.improvement_week,
                "improvement_month": skill_profile.improvement_month,
            },
            "achievements": [
                {
                    "type": a.achievement_type,
                    "title": a.title,
                    "rarity": a.rarity,
                    "earned_at": a.earned_at.isoformat(),
                }
                for a in achievements
            ],
            "streaks": [
                {
                    "type": s.streak_type,
                    "current": s.current_count,
                    "longest": s.longest_count,
                }
                for s in streaks
            ],
            "recent_milestones": [
                {
                    "title": m.title,
                    "type": m.milestone_type,
                    "metric_value": m.metric_value,
                    "achieved_at": m.achieved_at.isoformat(),
                }
                for m in recent_milestones
            ],
            "progress_trend": [
                {
                    "date": s.snapshot_date.isoformat(),
                    "avg_wpm": s.avg_wpm,
                    "avg_accuracy": s.avg_accuracy,
                    "total_sessions": s.total_sessions,
                    "week_improvement": s.week_improvement_pct,
                }
                for s in snapshots
            ],
        }

    def get_keyboard_heatmap(self, user_id: int) -> Dict:
        """Get keyboard heatmap data for visualization."""
        skill_profile = (
            self.db.query(UserSkillProfile)
            .filter(UserSkillProfile.user_id == user_id)
            .first()
        )

        if not skill_profile:
            return {}

        # Get latest snapshot
        latest_snapshot = (
            self.db.query(ProgressSnapshot)
            .filter(ProgressSnapshot.user_id == user_id)
            .order_by(ProgressSnapshot.snapshot_date.desc())
            .first()
        )

        if latest_snapshot:
            return latest_snapshot.keyboard_heatmap

        # Fall back to skill profile weak keys
        heatmap = {}
        for char, data in skill_profile.weak_keys.items():
            if isinstance(data, dict):
                heatmap[char] = data.get("error_rate", 0)

        return heatmap
