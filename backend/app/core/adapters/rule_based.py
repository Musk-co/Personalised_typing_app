"""
Rule-based typing adaptation engine.
Uses simple heuristics and thresholds for recommendations.
Perfect for MVP and non-ML systems.
"""

from typing import List, Optional
from app.core.adapters.base import BaseAdapter, AdapterRecommendation


class RuleBasedAdapter(BaseAdapter):
    """
    Rule-based adapter using configurable thresholds.
    
    Configuration parameters:
    - accuracy_threshold: % accuracy to consider success (default: 85)
    - wpm_threshold: WPM to consider success (default: 40)
    - error_threshold: Max errors before difficulty adjustment (default: 5)
    - improvement_rate: Sessions until difficulty increase (default: 2)
    """

    def __init__(self, config: Optional[dict] = None):
        """Initialize rule-based adapter with default thresholds."""
        super().__init__(config)
        
        # Set defaults
        self.accuracy_threshold = self.config.get("accuracy_threshold", 85)
        self.wpm_threshold = self.config.get("wpm_threshold", 40)
        self.error_threshold = self.config.get("error_threshold", 5)
        self.improvement_rate = self.config.get("improvement_rate", 2)

    def get_initial_difficulty(self, user_profile: dict) -> int:
        """
        Determine initial difficulty based on user experience.
        
        - New users: Level 1
        - Experienced users: Level 3
        - Advanced users: Level 5
        """
        experience = user_profile.get("experience_level", "beginner")
        
        if experience == "advanced":
            return 5
        elif experience == "intermediate":
            return 3
        else:
            return 1

    def analyze_session(self, session_data: dict) -> dict:
        """
        Analyze session using rule-based logic.
        """
        wpm = session_data.get("wpm", 0)
        accuracy = session_data.get("accuracy", 0)
        errors = session_data.get("errors", 0)
        
        # Determine performance level
        if accuracy >= self.accuracy_threshold and wpm >= self.wpm_threshold:
            performance = "excellent"
            confidence = 0.9
        elif accuracy >= 75 and wpm >= 30:
            performance = "good"
            confidence = 0.7
        elif accuracy >= 60:
            performance = "fair"
            confidence = 0.5
        else:
            performance = "needs_improvement"
            confidence = 0.3
        
        # Identify weak areas
        weak_areas = []
        key_stats = session_data.get("key_stats", {})
        
        for key, stats in key_stats.items():
            error_rate = stats.get("errors", 0) / max(stats.get("attempts", 1), 1)
            if error_rate > 0.1:  # More than 10% error rate
                weak_areas.append(f"Key: {key}")
        
        strong_areas = []
        for key, stats in key_stats.items():
            error_rate = stats.get("errors", 0) / max(stats.get("attempts", 1), 1)
            if error_rate < 0.02:  # Less than 2% error rate
                strong_areas.append(f"Key: {key}")
        
        return {
            "performance_level": performance,
            "confidence": confidence,
            "weak_areas": weak_areas,
            "strong_areas": strong_areas,
        }

    def recommend_next_difficulty(
        self,
        user_history: List[dict],
        current_performance: dict,
    ) -> AdapterRecommendation:
        """
        Recommend difficulty using rule-based logic.
        
        Rules:
        1. If last 2 sessions excellent → increase difficulty
        2. If accuracy < 60% → decrease difficulty
        3. Otherwise → maintain difficulty
        """
        if not user_history:
            return AdapterRecommendation(
                next_difficulty=1,
                focus_areas=["Get comfortable with basics"],
                reason="New user",
                confidence=1.0,
            )
        
        current_difficulty = user_history[-1].get("difficulty_level", 1)
        perf = current_performance.get("performance_level", "fair")
        
        # Count recent excellent sessions
        recent_excellent = sum(
            1
            for session in user_history[-self.improvement_rate :]
            if session.get("performance_level") == "excellent"
        )
        
        if recent_excellent >= self.improvement_rate and current_difficulty < 10:
            next_difficulty = min(current_difficulty + 1, 10)
            reason = f"Excellent performance in last {self.improvement_rate} sessions"
            confidence = 0.85
        elif perf == "needs_improvement" and current_difficulty > 1:
            next_difficulty = max(current_difficulty - 1, 1)
            reason = "Performance below threshold, reducing difficulty"
            confidence = 0.8
        else:
            next_difficulty = current_difficulty
            reason = "Maintaining current difficulty"
            confidence = 0.7
        
        # Focus areas based on weak areas
        focus_areas = current_performance.get("weak_areas", [])
        if not focus_areas:
            focus_areas = ["Continue building consistency"]
        
        return AdapterRecommendation(
            next_difficulty=next_difficulty,
            focus_areas=focus_areas,
            reason=reason,
            confidence=confidence,
        )

    def get_real_time_feedback(self, current_stats: dict) -> Optional[str]:
        """
        Provide real-time feedback during session.
        """
        accuracy = current_stats.get("accuracy", 0)
        wpm = current_stats.get("wpm", 0)
        
        if accuracy < 70:
            return "⚠️ Focus on accuracy - slow down if needed"
        elif wpm < self.wpm_threshold and accuracy >= 85:
            return "💨 You're accurate! Try to increase your speed"
        elif accuracy >= 90 and wpm >= self.wpm_threshold:
            return "🔥 Excellent! You're in the zone"
        
        return None
