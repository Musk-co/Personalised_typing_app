"""
Placement Test Service

Rapid assessment to classify users and set initial difficulty.

Placement tests are brief (5-10 minutes) and determine user's starting level.
Results drive initial difficulty and exercise selection.
"""

from typing import List, Optional
from enum import Enum
import random

from app.core.engine.exercise_generator import ExerciseGenerator, ExercisePrompt, ExerciseType
from app.core.engine.adaptation_engine import UserLevel


class PlacementTestLevel(str, Enum):
    """Placement test difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class PlacementTestService:
    """
    Generates and evaluates placement tests.
    
    Quick assessment to rapidly classify users and set starting parameters.
    """

    def __init__(self):
        self.generator = ExerciseGenerator()

    def generate_placement_test(self, test_level: PlacementTestLevel = PlacementTestLevel.MEDIUM) -> List[ExercisePrompt]:
        """
        Generate a placement test with 3 difficulty levels.
        
        User attempts all three, and we measure where they're comfortable.
        
        Args:
            test_level: Starting difficulty
            
        Returns:
            List of ExercisePrompt objects for placement test
        """
        test_exercises = []

        # Exercise 1: Easy (Beginner assessment)
        easy_text = self.generator.generate_mixed_exercise(
            weak_keys={},  # No weak keys yet
            error_patterns={},
            difficulty=2,
            duration_seconds=30
        )
        easy_text.description = "Placement Test - Part 1 (Easy)"
        test_exercises.append(easy_text)

        # Exercise 2: Medium (Intermediate assessment)
        medium_text = self.generator.generate_mixed_exercise(
            weak_keys={},
            error_patterns={},
            difficulty=5,
            duration_seconds=40
        )
        medium_text.description = "Placement Test - Part 2 (Medium)"
        test_exercises.append(medium_text)

        # Exercise 3: Hard (Advanced assessment)
        hard_text = self.generator.generate_mixed_exercise(
            weak_keys={},
            error_patterns={},
            difficulty=8,
            duration_seconds=50
        )
        hard_text.description = "Placement Test - Part 3 (Hard)"
        test_exercises.append(hard_text)

        return test_exercises

    def evaluate_placement_test(
        self,
        results: List[dict],  # [{level: "easy", accuracy: 95, wpm: 45}, ...]
    ) -> tuple:
        """
        Evaluate placement test results and classify user.
        
        Args:
            results: List of test results for each level
                     Each item: {level: "easy/medium/hard", accuracy: 0-100, wpm: float}
                     
        Returns:
            Tuple of (user_level, recommended_difficulty, confidence)
        """
        if not results or len(results) < 3:
            # Default to intermediate if incomplete
            return UserLevel.INTERMEDIATE, 5, 0.5

        # Score each level
        scores = {}
        for result in results:
            level = result['level']
            accuracy = result['accuracy']
            wpm = result['wpm']

            # Scoring: accuracy weighted 70%, wpm weighted 30%
            # To "pass" a level: accuracy > 90% AND wpm > baseline for level
            score = (accuracy * 0.7) + (self._normalize_wpm(wpm, level) * 0.3)
            scores[level] = score

        # Determine user level based on highest passed level
        easy_score = scores.get('easy', 0)
        medium_score = scores.get('medium', 0)
        hard_score = scores.get('hard', 0)

        # Simple decision tree
        if hard_score > 85:
            # User passed hard level - advanced
            user_level = UserLevel.ADVANCED
            difficulty = 7
            confidence = min(hard_score / 100, 1.0)
        elif medium_score > 85:
            # User passed medium level - intermediate
            user_level = UserLevel.INTERMEDIATE
            difficulty = 5
            confidence = min(medium_score / 100, 1.0)
        else:
            # User struggled on medium - beginner
            user_level = UserLevel.BEGINNER
            difficulty = 2
            confidence = 0.6

        return user_level, difficulty, confidence

    def _normalize_wpm(self, wpm: float, level: str) -> float:
        """
        Normalize WPM score for a level.
        
        Maps WPM to 0-100 score based on level expectations.
        """
        level_targets = {
            'easy': 25,    # Target 25 WPM for easy level
            'medium': 40,  # Target 40 WPM for medium
            'hard': 55,    # Target 55 WPM for hard
        }

        target = level_targets.get(level, 40)

        # Score: (wpm / target) * 100, capped at 100
        normalized = (wpm / target) * 100
        return min(normalized, 100)

    def quick_assessment(self) -> ExercisePrompt:
        """
        Generate a quick 2-minute assessment.
        
        Even faster than full placement test.
        Can be used to update classification.
        
        Returns:
            Single ExercisePrompt for quick assessment
        """
        return self.generator.generate_mixed_exercise(
            weak_keys={},
            error_patterns={},
            difficulty=4,
            duration_seconds=120
        )

    # Static helpers for placement test recommendations

    @staticmethod
    def get_starting_difficulty(user_level: UserLevel) -> int:
        """Get recommended starting difficulty for user level."""
        mapping = {
            UserLevel.BEGINNER: 2,
            UserLevel.INTERMEDIATE: 5,
            UserLevel.ADVANCED: 7,
        }
        return mapping.get(user_level, 5)

    @staticmethod
    def get_starting_exercise_type(user_level: UserLevel) -> str:
        """Get recommended starting exercise type for user level."""
        mapping = {
            UserLevel.BEGINNER: "accuracy_focus",
            UserLevel.INTERMEDIATE: "mixed",
            UserLevel.ADVANCED: "speed_challenge",
        }
        return mapping.get(user_level, "mixed")

    @staticmethod
    def user_needs_placement_test(total_sessions: int) -> bool:
        """
        Determine if user needs a placement test.
        
        Users new to system or returning after break should test.
        """
        return total_sessions == 0
