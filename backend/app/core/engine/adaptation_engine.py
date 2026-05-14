"""
Adaptation Engine

Rule-based logic for dynamically adjusting difficulty and generating recommendations.
Designed with Adapter pattern - interface allows swapping rule-based for ML-based logic.

Philosophy: "This system responds to ME" - difficulty adapts in real-time based on performance.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum
from abc import ABC, abstractmethod


class Difficulty(int, Enum):
    """Difficulty level (1-10)."""
    BEGINNER = 1
    EASY = 2
    EASY_MEDIUM = 3
    MEDIUM = 4
    MEDIUM_HARD = 5
    HARD = 6
    HARD_PLUS = 7
    VERY_HARD = 8
    EXTREME = 9
    INSANE = 10


class UserLevel(str, Enum):
    """User skill classification."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class AdaptationRecommendation:
    """Recommendation from adaptation engine."""
    next_difficulty: int  # 1-10
    difficulty_change: str  # "increase", "maintain", "decrease"
    exercise_type: str  # weak_key_drill, error_pattern, speed_challenge, etc.
    rationale: str  # Why this recommendation
    should_review_weak_keys: bool  # Should we do weak key drill?
    suggested_duration_seconds: int  # How long this exercise should be


class AdaptationEngineInterface(ABC):
    """
    Interface for adaptation engines.
    
    Allows swapping rule-based for ML-based engines seamlessly.
    """

    @abstractmethod
    def get_recommendation(
        self,
        current_difficulty: int,
        accuracy: float,
        wpm: float,
        consistency_score: float,
        error_rate: Optional[float] = None,
    ) -> AdaptationRecommendation:
        """
        Get adaptation recommendation.
        
        Args:
            current_difficulty: Current difficulty (1-10)
            accuracy: Current accuracy (0-100)
            wpm: Current WPM
            consistency_score: Score showing consistency (0-100)
            error_rate: Optional overall error rate
            
        Returns:
            AdaptationRecommendation with next difficulty and exercise type
        """
        pass

    @abstractmethod
    def classify_user_level(
        self,
        avg_wpm: float,
        avg_accuracy: float,
        total_sessions: int,
    ) -> UserLevel:
        """
        Classify user as Beginner/Intermediate/Advanced.
        
        Args:
            avg_wpm: Average WPM across sessions
            avg_accuracy: Average accuracy across sessions
            total_sessions: Total sessions completed
            
        Returns:
            UserLevel classification
        """
        pass


class RuleBasedAdaptationEngine(AdaptationEngineInterface):
    """
    Rule-based adaptation engine using simple thresholds.
    
    Easy to understand, fast, and provides baseline behavior.
    Can be replaced with ML engine that uses same interface.
    """

    # Thresholds for difficulty adjustment
    ACCURACY_TOO_LOW = 85.0  # If below this, decrease difficulty
    ACCURACY_GOOD = 92.0    # If above this, can increase
    ACCURACY_EXCELLENT = 98.0  # If above this, increase aggressively

    WPM_TARGET_MULTIPLIER = 1.5  # Target WPM for current difficulty

    CONSISTENCY_THRESHOLD = 65.0  # Score above this means stable performance

    def get_recommendation(
        self,
        current_difficulty: int,
        accuracy: float,
        wpm: float,
        consistency_score: float,
        error_rate: Optional[float] = None,
    ) -> AdaptationRecommendation:
        """
        Get difficulty recommendation based on performance.
        
        Rules:
        1. Accuracy is primary metric
        2. Consistency determines confidence in recommendation
        3. WPM suggests headroom for increase
        4. Exercise type depends on what's weak
        """

        next_difficulty = current_difficulty
        difficulty_change = "maintain"
        rationale = ""
        exercise_type = "mixed"

        # Rule 1: Accuracy too low - decrease difficulty
        if accuracy < self.ACCURACY_TOO_LOW:
            next_difficulty = max(1, current_difficulty - 1)
            difficulty_change = "decrease"
            rationale = f"Accuracy is {accuracy:.1f}% - need to focus on precision before speed"
            exercise_type = "accuracy_focus"

        # Rule 2: Accuracy excellent - increase difficulty
        elif accuracy > self.ACCURACY_EXCELLENT:
            next_difficulty = min(10, current_difficulty + 2)
            difficulty_change = "increase"
            rationale = f"Accuracy {accuracy:.1f}% is excellent - time to push speed"
            exercise_type = "speed_challenge"

        # Rule 3: Accuracy good - conditional increase based on consistency
        elif accuracy > self.ACCURACY_GOOD:
            if consistency_score > self.CONSISTENCY_THRESHOLD:
                next_difficulty = min(10, current_difficulty + 1)
                difficulty_change = "increase"
                rationale = f"Solid accuracy ({accuracy:.1f}%) and consistent - ready to advance"
                exercise_type = "mixed"
            else:
                difficulty_change = "maintain"
                rationale = f"Accuracy is good but inconsistent (score: {consistency_score:.0f}%) - stabilize first"
                exercise_type = "weak_key_drill"

        # Rule 4: Maintain with weak key focus
        else:
            difficulty_change = "maintain"
            rationale = f"Accuracy {accuracy:.1f}% - maintaining current difficulty with weak key focus"
            exercise_type = "weak_key_drill"

        # Suggested duration based on difficulty
        suggested_duration = 30 + (min(current_difficulty, next_difficulty) * 5)

        return AdaptationRecommendation(
            next_difficulty=next_difficulty,
            difficulty_change=difficulty_change,
            exercise_type=exercise_type,
            rationale=rationale,
            should_review_weak_keys=(exercise_type == "weak_key_drill" or accuracy < self.ACCURACY_GOOD),
            suggested_duration_seconds=suggested_duration,
        )

    def classify_user_level(
        self,
        avg_wpm: float,
        avg_accuracy: float,
        total_sessions: int,
    ) -> UserLevel:
        """
        Classify user skill level.
        
        Based on WPM and accuracy thresholds.
        """

        # Beginner: WPM < 30 or low accuracy
        if avg_wpm < 30 or avg_accuracy < 88:
            return UserLevel.BEGINNER

        # Intermediate: 30-50 WPM, decent accuracy
        if avg_wpm < 50:
            return UserLevel.INTERMEDIATE

        # Advanced: 50+ WPM, high accuracy
        return UserLevel.ADVANCED


class MLAdaptationEngine(AdaptationEngineInterface):
    """
    ML-based adaptation engine (placeholder for future).
    
    When integrated, this will use ML models trained on user data
    to provide smarter, more personalized recommendations.
    
    For now, this is a stub that can be implemented later.
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize ML engine.
        
        Args:
            model_path: Path to trained ML model (future)
        """
        self.model_path = model_path
        self.model = None  # Placeholder for actual model loading

    def get_recommendation(
        self,
        current_difficulty: int,
        accuracy: float,
        wpm: float,
        consistency_score: float,
        error_rate: Optional[float] = None,
    ) -> AdaptationRecommendation:
        """
        Get recommendation using ML model.
        
        When implemented, this will:
        1. Extract features from performance history
        2. Feed through trained model
        3. Get probabilistic difficulty recommendation
        4. Select exercise type based on weakness patterns
        """
        raise NotImplementedError("ML engine not yet implemented")

    def classify_user_level(
        self,
        avg_wpm: float,
        avg_accuracy: float,
        total_sessions: int,
    ) -> UserLevel:
        """
        Classify user level using ML.
        
        When implemented, will use learned patterns.
        """
        raise NotImplementedError("ML engine not yet implemented")


class AdaptationEngineFactory:
    """
    Factory for creating adaptation engines.
    
    Simplifies swapping between rule-based and ML-based engines.
    """

    @staticmethod
    def create_engine(engine_type: str = "rule_based") -> AdaptationEngineInterface:
        """
        Create adaptation engine of specified type.
        
        Args:
            engine_type: "rule_based" or "ml"
            
        Returns:
            Appropriate engine instance
        """
        if engine_type == "rule_based":
            return RuleBasedAdaptationEngine()
        elif engine_type == "ml":
            return MLAdaptationEngine()
        else:
            raise ValueError(f"Unknown engine type: {engine_type}")

    @staticmethod
    def create_default_engine() -> AdaptationEngineInterface:
        """Create the default (rule-based) engine."""
        return RuleBasedAdaptationEngine()
