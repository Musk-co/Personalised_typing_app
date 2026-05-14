"""
Skill Profile Service

Updates and manages user skill profiles based on keystroke data.
Handles:
- Creating/updating user skill profiles
- Calculating rolling averages from session history
- Tracking weak keys and error patterns
- Generating insights
- Creating skill snapshots for time-series analysis

This service makes the profile "alive" - updating dynamically after each session.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.db.models import (
    UserSkillProfile,
    SkillSnapshot,
    WeakKeyProfile,
    ErrorPatternProfile,
    UserSkillInsight,
    TypingSession,
    Keystroke,
)
from app.core.engine.skill_calculator import SkillCalculator, InsightType, InsightTone


class SkillProfileService:
    """
    Service for managing user skill profiles.
    
    The "heart" of personalization - evolves dynamically with each session.
    Makes users feel known and understood through data-driven insights.
    """

    def __init__(self, db: Session):
        self.db = db
        self.calculator = SkillCalculator(window_size=5)

    def update_skill_profile_for_session(
        self,
        user_id: int,
        session_id: int,
    ) -> Optional[UserSkillProfile]:
        """
        Update user's skill profile after a session completes.
        
        Process:
        1. Fetch session and keystroke data
        2. Calculate metrics
        3. Update aggregated profile
        4. Update weak keys
        5. Update error patterns
        6. Generate insights
        7. Create snapshot for trend analysis
        
        Args:
            user_id: User ID
            session_id: Completed session ID
            
        Returns:
            Updated UserSkillProfile or None if failed
        """
        
        # Verify session exists and belongs to user
        session = self.db.query(TypingSession).filter(
            and_(
                TypingSession.id == session_id,
                TypingSession.user_id == user_id
            )
        ).first()
        
        if not session:
            return None
        
        # Fetch keystroke data for this session
        keystrokes = self.db.query(Keystroke).filter(
            Keystroke.session_id == session_id
        ).all()
        
        if not keystrokes:
            return None
        
        keystroke_data = [
            {
                'character': k.character,
                'expected_character': k.expected_character,
                'position': k.position,
                'timestamp_ms': k.timestamp_ms,
                'is_correct': k.is_correct,
                'error_type': k.error_type,
            }
            for k in keystrokes
        ]
        
        # Get or create user skill profile
        profile = self.db.query(UserSkillProfile).filter(
            UserSkillProfile.user_id == user_id
        ).first()
        
        if not profile:
            profile = UserSkillProfile(user_id=user_id)
            self.db.add(profile)
        
        # Fetch recent sessions for rolling averages
        recent_sessions = self._get_recent_sessions(user_id, limit=5)
        
        # Calculate aggregated metrics
        wpm = self.calculator.calculate_wpm(
            len(keystroke_data),
            (session.duration_seconds or 60)
        )
        
        correct_count = sum(1 for k in keystroke_data if k['is_correct'])
        accuracy = self.calculator.calculate_accuracy(
            correct_count,
            len(keystroke_data)
        )
        
        # Get recent WPMs for rolling average
        recent_wpms = [wpm]
        for recent_session in recent_sessions:
            if recent_session.wpm:
                recent_wpms.append(recent_session.wpm)
        
        recent_accuracies = [accuracy]
        for recent_session in recent_sessions:
            if recent_session.accuracy:
                recent_accuracies.append(recent_session.accuracy)
        
        # Calculate rolling averages
        avg_wpm = self.calculator.calculate_rolling_average(recent_wpms)
        avg_accuracy = self.calculator.calculate_rolling_average(recent_accuracies)
        
        # Identify weak keys
        weak_keys = self.calculator.identify_weak_keys(keystroke_data)
        
        # Aggregate error patterns
        error_patterns = self.calculator.aggregate_error_patterns(keystroke_data)
        
        # Calculate consistency
        consistency = self.calculator.calculate_consistency_score(recent_wpms)
        
        # Calculate improvements
        prev_wpm = recent_wpms[1] if len(recent_wpms) > 1 else None
        improvement_week = None
        if prev_wpm:
            improvement_week = self.calculator.calculate_improvement(wpm, prev_wpm)
        
        # Update profile
        profile.avg_wpm = avg_wpm
        profile.avg_accuracy = avg_accuracy
        profile.total_sessions = profile.total_sessions + 1
        profile.total_keystrokes = profile.total_keystrokes + len(keystroke_data)
        profile.total_errors = profile.total_errors + (
            len(keystroke_data) - correct_count
        )
        profile.weak_keys = weak_keys
        profile.error_patterns = error_patterns
        profile.improvement_week = improvement_week
        profile.consistency_score = consistency
        
        # Update best scores
        if profile.best_wpm is None or wpm > profile.best_wpm:
            profile.best_wpm = wpm
        if profile.best_accuracy is None or accuracy > profile.best_accuracy:
            profile.best_accuracy = accuracy
        
        # Update streaks
        if correct_count == len(keystroke_data):
            # Perfect session
            profile.current_streak = (profile.current_streak or 0) + 1
            if (profile.longest_streak or 0) < profile.current_streak:
                profile.longest_streak = profile.current_streak
        else:
            profile.current_streak = 0
        
        # Commit profile update
        self.db.commit()
        
        # Update weak key profiles
        self._update_weak_key_profiles(user_id, keystroke_data)
        
        # Update error pattern profiles
        self._update_error_pattern_profiles(user_id, keystroke_data)
        
        # Generate insights
        self._generate_insights_for_profile(user_id, profile)
        
        # Create snapshot for trend analysis
        self._create_skill_snapshot(user_id, session_id, profile, wpm, accuracy)
        
        return profile

    def get_user_skill_profile(self, user_id: int) -> Optional[UserSkillProfile]:
        """
        Get user's current skill profile.
        
        Args:
            user_id: User ID
            
        Returns:
            UserSkillProfile or None
        """
        return self.db.query(UserSkillProfile).filter(
            UserSkillProfile.user_id == user_id
        ).first()

    def get_skill_history(
        self,
        user_id: int,
        days: int = 30
    ) -> List[SkillSnapshot]:
        """
        Get skill progression snapshots over time period.
        
        Args:
            user_id: User ID
            days: Number of days to look back (default 30)
            
        Returns:
            List of SkillSnapshots
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(SkillSnapshot).filter(
            and_(
                SkillSnapshot.user_id == user_id,
                SkillSnapshot.snapshot_date >= since
            )
        ).order_by(SkillSnapshot.snapshot_date).all()

    def get_weak_keys_profile(self, user_id: int) -> List[WeakKeyProfile]:
        """
        Get detailed weak key profiles for user.
        
        Returns keys sorted by error rate (worst first).
        
        Args:
            user_id: User ID
            
        Returns:
            List of WeakKeyProfiles
        """
        return self.db.query(WeakKeyProfile).filter(
            WeakKeyProfile.user_id == user_id
        ).order_by(desc(WeakKeyProfile.error_rate)).all()

    def get_error_patterns_profile(self, user_id: int) -> List[ErrorPatternProfile]:
        """
        Get user's error pattern profiles.
        
        Args:
            user_id: User ID
            
        Returns:
            List of ErrorPatternProfiles
        """
        return self.db.query(ErrorPatternProfile).filter(
            ErrorPatternProfile.user_id == user_id
        ).order_by(desc(ErrorPatternProfile.total_occurrences)).all()

    def get_active_insights(self, user_id: int) -> List[UserSkillInsight]:
        """
        Get active insights for user (prioritized).
        
        Args:
            user_id: User ID
            
        Returns:
            List of insights sorted by priority
        """
        return self.db.query(UserSkillInsight).filter(
            and_(
                UserSkillInsight.user_id == user_id,
                UserSkillInsight.is_active == True
            )
        ).order_by(desc(UserSkillInsight.priority)).all()

    # Private helper methods

    def _get_recent_sessions(
        self,
        user_id: int,
        limit: int = 5
    ) -> List[TypingSession]:
        """Fetch user's recent completed sessions."""
        return self.db.query(TypingSession).filter(
            and_(
                TypingSession.user_id == user_id,
                TypingSession.status == 'completed'
            )
        ).order_by(desc(TypingSession.ended_at)).limit(limit).all()

    def _update_weak_key_profiles(
        self,
        user_id: int,
        keystroke_data: List[Dict]
    ) -> None:
        """Update weak key profiles based on keystroke data."""
        
        # Build character statistics
        char_stats = {}
        for keystroke in keystroke_data:
            char = keystroke.get('expected_character') or keystroke.get('character')
            if not char:
                continue
            
            if char not in char_stats:
                char_stats[char] = {
                    'attempts': 0,
                    'errors': 0,
                    'error_types': {}
                }
            
            char_stats[char]['attempts'] += 1
            if not keystroke.get('is_correct'):
                char_stats[char]['errors'] += 1
                error_type = keystroke.get('error_type')
                if error_type:
                    char_stats[char]['error_types'][error_type] = (
                        char_stats[char]['error_types'].get(error_type, 0) + 1
                    )
        
        # Update or create weak key profiles
        for char, stats in char_stats.items():
            profile = self.db.query(WeakKeyProfile).filter(
                and_(
                    WeakKeyProfile.user_id == user_id,
                    WeakKeyProfile.character == char
                )
            ).first()
            
            if not profile:
                profile = WeakKeyProfile(
                    user_id=user_id,
                    character=char
                )
                self.db.add(profile)
            
            # Update stats
            profile.total_attempts += stats['attempts']
            profile.total_errors += stats['errors']
            profile.error_rate = (
                profile.total_errors / profile.total_attempts
                if profile.total_attempts > 0 else 0.0
            )
            profile.error_distribution = stats['error_types']
            
            # Update recent stats (last 5 sessions)
            profile.recent_attempts = stats['attempts']
            profile.recent_errors = stats['errors']
            profile.recent_error_rate = (
                stats['errors'] / stats['attempts']
                if stats['attempts'] > 0 else 0.0
            )
            
            # Determine trend
            if profile.recent_error_rate < profile.error_rate * 0.8:
                profile.trend = 'improving'
            elif profile.recent_error_rate > profile.error_rate * 1.2:
                profile.trend = 'declining'
            else:
                profile.trend = 'stable'
            
            profile.last_updated = datetime.utcnow()
        
        self.db.commit()

    def _update_error_pattern_profiles(
        self,
        user_id: int,
        keystroke_data: List[Dict]
    ) -> None:
        """Update error pattern profiles."""
        
        error_patterns = {}
        
        for keystroke in keystroke_data:
            error_type = keystroke.get('error_type')
            if not error_type:
                continue
            
            if error_type not in error_patterns:
                error_patterns[error_type] = {
                    'count': 0,
                    'details': {}
                }
            
            error_patterns[error_type]['count'] += 1
            
            # Extract pattern detail
            expected = keystroke.get('expected_character')
            actual = keystroke.get('character')
            
            if error_type == 'substitution' and expected and actual:
                key = f"{expected}->{actual}"
                error_patterns[error_type]['details'][key] = (
                    error_patterns[error_type]['details'].get(key, 0) + 1
                )
        
        total_errors = sum(p['count'] for p in error_patterns.values())
        
        for error_type, data in error_patterns.items():
            profile = self.db.query(ErrorPatternProfile).filter(
                and_(
                    ErrorPatternProfile.user_id == user_id,
                    ErrorPatternProfile.error_type == error_type
                )
            ).first()
            
            if not profile:
                profile = ErrorPatternProfile(
                    user_id=user_id,
                    error_type=error_type
                )
                self.db.add(profile)
            
            profile.total_occurrences += data['count']
            profile.percentage = (
                (profile.total_occurrences / total_errors * 100)
                if total_errors > 0 else 0.0
            )
            profile.pattern_details = data['details']
            profile.sessions_with_error += 1
            profile.last_observed = datetime.utcnow()
        
        self.db.commit()

    def _generate_insights_for_profile(
        self,
        user_id: int,
        profile: UserSkillProfile
    ) -> None:
        """Generate insights based on updated profile."""
        
        insight_types = [
            InsightType.STRENGTH,
            InsightType.WEAKNESS,
            InsightType.IMPROVEMENT,
            InsightType.PATTERN,
            InsightType.MILESTONE
        ]
        
        for insight_type in insight_types:
            insight_data = self.calculator.generate_coaching_insight(
                {
                    'avg_wpm': profile.avg_wpm,
                    'avg_accuracy': profile.avg_accuracy,
                    'total_sessions': profile.total_sessions,
                    'total_keystrokes': profile.total_keystrokes,
                    'total_errors': profile.total_errors,
                    'weak_keys': profile.weak_keys,
                    'error_patterns': profile.error_patterns,
                    'improvement_week': profile.improvement_week,
                    'improvement_month': profile.improvement_month,
                    'consistency_score': profile.consistency_score,
                    'best_wpm': profile.best_wpm,
                    'best_accuracy': profile.best_accuracy,
                    'current_streak': profile.current_streak,
                },
                insight_type
            )
            
            if insight_data:
                # Check if similar insight exists
                existing = self.db.query(UserSkillInsight).filter(
                    and_(
                        UserSkillInsight.user_id == user_id,
                        UserSkillInsight.insight_type == insight_type.value
                    )
                ).first()
                
                if existing:
                    # Update existing
                    existing.description = insight_data['description']
                    existing.metric_value = insight_data.get('metric_value')
                    existing.last_seen = datetime.utcnow()
                else:
                    # Create new
                    insight = UserSkillInsight(
                        user_id=user_id,
                        insight_type=insight_type.value,
                        title=insight_data['title'],
                        description=insight_data['description'],
                        metric_name=insight_data.get('metric_name'),
                        metric_value=insight_data.get('metric_value'),
                        recommendation=insight_data.get('recommendation'),
                        tone=insight_data.get('tone', 'encouraging'),
                        priority=insight_data.get('priority', 5)
                    )
                    self.db.add(insight)
        
        self.db.commit()

    def _create_skill_snapshot(
        self,
        user_id: int,
        session_id: int,
        profile: UserSkillProfile,
        session_wpm: float,
        session_accuracy: float
    ) -> None:
        """Create snapshot for time-series trend analysis."""
        
        # Get previous snapshot for comparison
        previous = self.db.query(SkillSnapshot).filter(
            SkillSnapshot.user_id == user_id
        ).order_by(desc(SkillSnapshot.created_at)).first()
        
        wpm_change = None
        accuracy_change = None
        
        if previous:
            wpm_change = session_wpm - previous.wpm
            accuracy_change = session_accuracy - previous.accuracy
        
        snapshot = SkillSnapshot(
            user_id=user_id,
            session_id=session_id,
            wpm=session_wpm,
            accuracy=session_accuracy,
            total_sessions=profile.total_sessions,
            cumulative_wpm_avg=profile.avg_wpm,
            cumulative_accuracy_avg=profile.avg_accuracy,
            cumulative_errors=profile.total_errors,
            weak_keys_snapshot=profile.weak_keys,
            error_pattern_snapshot=profile.error_patterns,
            wpm_change=wpm_change,
            accuracy_change=accuracy_change
        )
        
        self.db.add(snapshot)
        self.db.commit()
