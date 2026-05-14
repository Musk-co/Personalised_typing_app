"""
Core typing evaluation engine.
Processes user input and calculates detailed metrics.
Integrates error classification with Levenshtein distance analysis.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from .error_detector import ErrorClassifier, LevenshteinCalculator


@dataclass
class TypingError:
    """Represents a single typing error."""
    position: int  # Position in text
    expected: str  # Expected character
    actual: str  # Actual character typed
    timestamp: float  # Seconds into session
    error_type: str  # substitution, insertion, deletion, transposition


class TypingEvaluator:
    """
    Advanced typing performance evaluation engine.
    Captures keystroke-level detail with error classification.
    
    Every keystroke is analyzed for:
    - Correct/incorrect classification
    - Error type (substitution, insertion, deletion, transposition)
    - Timing precision
    - Pattern analysis (weak keys, shift combinations, etc.)
    """

    def __init__(self):
        """Initialize evaluator."""
        self.errors: List[TypingError] = []
        self.key_stats: Dict[str, Dict] = {}

    def evaluate(
        self,
        expected_text: str,
        typed_text: str,
        duration_seconds: float,
        keystroke_events: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Perform comprehensive typing evaluation.
        
        Args:
            expected_text: Text user was supposed to type
            typed_text: Text user actually typed
            duration_seconds: Time taken
            keystroke_events: List of keystroke events with timestamps
            
        Returns:
            {
                'wpm': float,
                'accuracy': float,
                'errors': int,
                'key_presses': int,
                'levenshtein_distance': int,
                'error_details': {...},          # Detailed errors by position
                'error_classification': {...},   # Error type breakdown
                'key_stats': {...},              # Per-key statistics
                'error_timeline': [...],         # Timeline of errors
                'weak_keys': [str, ...],         # Keys with errors
                'character_classification': {}   # Each char: correct/incorrect
            }
        """
        self.errors = []
        self.key_stats = {}
        keystroke_events = keystroke_events or []
        
        # Classify each character as correct/incorrect
        char_classification = ErrorClassifier.get_character_classification(expected_text, typed_text)
        
        # Calculate basic metrics
        key_presses = len(typed_text)
        words = len(expected_text.split())
        minutes = duration_seconds / 60.0
        
        # WPM calculation (standard: 5 characters = 1 word)
        total_chars = len(expected_text)
        wpm = (total_chars / 5 / minutes) if minutes > 0 else 0
        
        # Calculate accuracy (proportion of correct characters)
        correct_chars = sum(1 for c in char_classification.values() if c["is_correct"])
        accuracy = (correct_chars / len(expected_text) * 100) if expected_text else 100.0
        accuracy = max(0, min(100, accuracy))
        
        # Perform detailed error analysis
        error_analysis = ErrorClassifier.analyze(expected_text, typed_text, keystroke_events)
        
        # Build error details (position-indexed)
        error_details = {}
        for error in error_analysis.error_details:
            error_details[error.position] = {
                "expected": error.expected_char,
                "actual": error.actual_char,
                "error_type": error.error_type.value,
                "timestamp_ms": error.timestamp_ms,
                "context": f"{error.context_before}[{error.expected_char}]{error.context_after}",
            }
        
        # Analyze per-key statistics
        key_stats = self._analyze_key_patterns(expected_text, char_classification, error_analysis)
        
        # Find weak keys (keys with errors)
        weak_keys = sorted(
            [k for k, v in key_stats.items() if v["errors"] > 0],
            key=lambda k: key_stats[k]["error_rate"],
            reverse=True
        )
        
        # Build error timeline (errors in order)
        error_timeline = [
            {
                "position": e.position,
                "expected": e.expected_char,
                "actual": e.actual_char,
                "error_type": e.error_type.value,
                "timestamp_ms": e.timestamp_ms,
            }
            for e in error_analysis.error_details
        ]
        
        # Build error classification summary
        error_classification = {
            "total": error_analysis.total_errors,
            "by_type": error_analysis.errors_by_type,
            "levenshtein_distance": error_analysis.levenshtein_distance,
        }
        
        return {
            "wpm": round(wpm, 2),
            "accuracy": round(accuracy, 2),
            "errors": error_analysis.total_errors,
            "key_presses": key_presses,
            "levenshtein_distance": error_analysis.levenshtein_distance,
            
            # Detailed error information
            "error_details": error_details,
            "error_classification": error_classification,
            "error_timeline": error_timeline,
            
            # Per-character and per-key analysis
            "key_stats": key_stats,
            "weak_keys": weak_keys,
            "character_classification": char_classification,
            
            # Metrics for adaptive engine
            "performance_indicators": {
                "speed_level": self._classify_speed(wpm),
                "accuracy_level": self._classify_accuracy(accuracy),
                "consistency": self._calculate_consistency(keystroke_events),
            }
        }

    def _analyze_key_patterns(
        self, 
        expected_text: str, 
        char_classification: Dict,
        error_analysis
    ) -> Dict:
        """
        Analyze typing patterns by key/character.
        
        Returns:
            {
                'a': {
                    'attempts': 5,
                    'correct': 4,
                    'errors': 1,
                    'error_rate': 0.2,
                    'error_types': {'substitution': 1}
                },
                ...
            }
        """
        key_stats = {}
        
        # Initialize stats for all characters in expected text
        for char in expected_text:
            if char not in key_stats:
                key_stats[char] = {
                    "attempts": 0,
                    "correct": 0,
                    "errors": 0,
                    "error_rate": 0.0,
                    "error_types": {},
                    "positions": [],
                }
        
        # Count occurrences and errors
        for i, char in enumerate(expected_text):
            key_stats[char]["attempts"] += 1
            key_stats[char]["positions"].append(i)
            
            if i in char_classification:
                classification = char_classification[i]
                if classification["is_correct"]:
                    key_stats[char]["correct"] += 1
                else:
                    key_stats[char]["errors"] += 1
                    error_type = classification.get("error_type", "unknown")
                    if error_type not in key_stats[char]["error_types"]:
                        key_stats[char]["error_types"][error_type] = 0
                    key_stats[char]["error_types"][error_type] += 1
        
        # Calculate error rates
        for char, stats in key_stats.items():
            if stats["attempts"] > 0:
                stats["error_rate"] = stats["errors"] / stats["attempts"]
        
        return key_stats

    def _classify_speed(self, wpm: float) -> str:
        """Classify typing speed level."""
        if wpm < 20:
            return "beginner"
        elif wpm < 40:
            return "intermediate"
        elif wpm < 60:
            return "advanced"
        else:
            return "expert"

    def _classify_accuracy(self, accuracy: float) -> str:
        """Classify accuracy level."""
        if accuracy >= 95:
            return "excellent"
        elif accuracy >= 85:
            return "good"
        elif accuracy >= 70:
            return "fair"
        else:
            return "needs_improvement"

    def _calculate_consistency(self, keystroke_events: List[Dict]) -> float:
        """
        Calculate typing consistency (variance of inter-keystroke intervals).
        Lower is more consistent.
        """
        if len(keystroke_events) < 2:
            return 0.0
        
        intervals = []
        for i in range(1, len(keystroke_events)):
            prev_time = keystroke_events[i - 1].get("timestamp_ms", 0)
            curr_time = keystroke_events[i].get("timestamp_ms", 0)
            interval = curr_time - prev_time
            if interval > 0:
                intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
        
        # Normalize to 0-1 scale (lower is more consistent)
        consistency = min(1.0, variance / 1000.0)
        return round(consistency, 2)
