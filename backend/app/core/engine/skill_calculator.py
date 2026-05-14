"""
Skill Calculator Service

Processes keystroke data from sessions and builds intelligent user skill profiles.
Handles:
- Rolling averages (WPM, accuracy)
- Weak key identification
- Error pattern tracking
- Skill trend analysis
- Insight generation

This is the intelligence engine that makes personalization feel genuine.
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class InsightType(Enum):
    """Types of coaching insights generated from skill data."""
    STRENGTH = "strength"
    WEAKNESS = "weakness"
    IMPROVEMENT = "improvement"
    PATTERN = "pattern"
    MILESTONE = "milestone"


class InsightTone(Enum):
    """Tone of insight - affects how user receives feedback."""
    ENCOURAGING = "encouraging"
    CAUTIONARY = "cautionary"
    CELEBRATORY = "celebratory"
    HONEST = "honest"


@dataclass
class SkillMetrics:
    """Container for calculated skill metrics."""
    avg_wpm: float
    avg_accuracy: float
    total_sessions: int
    total_keystrokes: int
    total_errors: int
    weak_keys: Dict[str, Dict[str, float]]  # {char: {frequency, error_rate}}
    error_patterns: Dict[str, int]  # {type: count}
    improvement_week: Optional[float]
    improvement_month: Optional[float]
    consistency_score: float
    best_wpm: Optional[float]
    best_accuracy: Optional[float]
    current_streak: int


@dataclass
class WeakKeyStats:
    """Stats for a single weak key."""
    character: str
    total_attempts: int
    total_errors: int
    error_rate: float
    error_distribution: Dict[str, int]
    recent_error_rate: float
    trend: str  # improving, stable, declining
    improvement_pct: Optional[float]


@dataclass
class ErrorPattern:
    """A detected error pattern."""
    error_type: str  # substitution, insertion, deletion, transposition
    total_occurrences: int
    percentage: float
    pattern_details: Dict[str, int]
    under_pressure: bool
    when_tired: bool


class SkillCalculator:
    """
    Calculates and aggregates user skill metrics from keystroke data.
    
    Key philosophy:
    - Smooth out noise with rolling averages
    - Show real trends with consistent data
    - Identify true weak keys vs. random errors
    - Generate actionable, non-judgmental insights
    """

    def __init__(self, window_size: int = 5):
        """
        Initialize calculator.
        
        Args:
            window_size: Number of sessions to include in rolling averages
        """
        self.window_size = window_size

    def calculate_wpm(self, keystrokes: int, duration_seconds: float) -> float:
        """
        Calculate WPM from keystrokes.
        
        WPM = (characters / 5) / minutes
        Standard typing metric where 5 characters = 1 "word"
        
        Args:
            keystrokes: Total characters typed
            duration_seconds: Time spent typing
            
        Returns:
            WPM as float
        """
        if duration_seconds <= 0:
            return 0.0
        
        minutes = duration_seconds / 60.0
        if minutes < 0.01:  # Avoid division by very small numbers
            return 0.0
        
        wpm = (keystrokes / 5.0) / minutes
        return round(wpm, 2)

    def calculate_accuracy(self, correct_keystrokes: int, total_keystrokes: int) -> float:
        """
        Calculate accuracy percentage.
        
        Accuracy = correct_keystrokes / total_keystrokes * 100
        
        Args:
            correct_keystrokes: Number of correct keystrokes
            total_keystrokes: Total keystrokes
            
        Returns:
            Accuracy as percentage (0-100)
        """
        if total_keystrokes == 0:
            return 100.0
        
        accuracy = (correct_keystrokes / total_keystrokes) * 100
        return round(min(accuracy, 100), 2)

    def calculate_rolling_average(
        self, 
        values: List[float], 
        window: Optional[int] = None
    ) -> float:
        """
        Calculate rolling average, smoothing noise.
        
        Args:
            values: List of values (e.g., WPM from last 5 sessions)
            window: Window size (default: self.window_size)
            
        Returns:
            Rolling average
        """
        if not values:
            return 0.0
        
        window = window or self.window_size
        recent = values[-window:] if len(values) >= window else values
        
        return round(sum(recent) / len(recent), 2)

    def calculate_consistency_score(self, values: List[float]) -> float:
        """
        Calculate consistency score (how stable is performance?).
        
        High consistency = reliable performer
        Low consistency = variable performance
        
        Calculated as: 100 - (std_dev / mean * 100)
        Bounded 0-100
        
        Args:
            values: List of recent performance values
            
        Returns:
            Consistency score (0-100)
        """
        if not values or len(values) < 2:
            return 100.0
        
        mean = sum(values) / len(values)
        if mean == 0:
            return 0.0
        
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        consistency = 100 - (std_dev / mean * 100)
        return round(max(0, min(100, consistency)), 2)

    def identify_weak_keys(
        self,
        keystroke_data: List[Dict]
    ) -> Dict[str, Dict[str, float]]:
        """
        Identify weak keys from keystroke data.
        
        Looks at:
        - Error frequency for each character
        - How often character is typed
        - Ranking by error rate
        
        Args:
            keystroke_data: List of keystroke records
            
        Returns:
            Dict mapping character to stats:
            {
                'a': {'frequency': 25, 'error_rate': 0.24},
                's': {'frequency': 15, 'error_rate': 0.13}
            }
        """
        char_stats = {}
        
        for keystroke in keystroke_data:
            char = keystroke.get('expected_character') or keystroke.get('character')
            if not char:
                continue
            
            if char not in char_stats:
                char_stats[char] = {'attempts': 0, 'errors': 0}
            
            char_stats[char]['attempts'] += 1
            if not keystroke.get('is_correct'):
                char_stats[char]['errors'] += 1
        
        # Calculate error rates and filter to actual weak keys
        weak_keys = {}
        for char, stats in char_stats.items():
            attempts = stats['attempts']
            errors = stats['errors']
            error_rate = errors / attempts if attempts > 0 else 0.0
            
            # Only flag as weak if:
            # 1. Has enough attempts to be meaningful (> 3)
            # 2. Error rate > 10%
            if attempts >= 3 and error_rate >= 0.10:
                weak_keys[char] = {
                    'frequency': attempts,
                    'error_rate': round(error_rate, 3)
                }
        
        # Sort by error rate (descending)
        sorted_weak = dict(
            sorted(
                weak_keys.items(),
                key=lambda x: x[1]['error_rate'],
                reverse=True
            )
        )
        
        return sorted_weak

    def aggregate_error_patterns(
        self,
        keystroke_data: List[Dict]
    ) -> Dict[str, int]:
        """
        Aggregate error types from keystroke data.
        
        Returns count of each error type:
        {
            'substitution': 145,
            'insertion': 89,
            'deletion': 32,
            'transposition': 18
        }
        
        Args:
            keystroke_data: List of keystroke records
            
        Returns:
            Dict mapping error type to count
        """
        error_counts = {
            'substitution': 0,
            'insertion': 0,
            'deletion': 0,
            'transposition': 0
        }
        
        for keystroke in keystroke_data:
            error_type = keystroke.get('error_type')
            if error_type and error_type in error_counts:
                error_counts[error_type] += 1
        
        return error_counts

    def calculate_improvement(
        self,
        current_value: float,
        previous_value: float
    ) -> Optional[float]:
        """
        Calculate percentage improvement between values.
        
        Args:
            current_value: Current metric value
            previous_value: Previous metric value
            
        Returns:
            Percentage change (positive = improvement for WPM)
        """
        if previous_value == 0:
            return None
        
        change = ((current_value - previous_value) / previous_value) * 100
        return round(change, 2)

    def detect_error_patterns(
        self,
        keystroke_data: List[Dict],
        is_high_speed: bool = False,
        is_late_session: bool = False
    ) -> List[ErrorPattern]:
        """
        Detect specific error patterns in user's typing.
        
        Identifies contextual patterns:
        - Substitution patterns (what char mistakes happen)
        - Insertion habits (what gets extra typed)
        - Deletion patterns (what gets skipped)
        - Transposition tendencies
        
        Args:
            keystroke_data: List of keystroke records
            is_high_speed: Whether this was high-speed typing
            is_late_session: Whether this was late in session
            
        Returns:
            List of detected patterns
        """
        patterns = {}
        error_count = 0
        
        for keystroke in keystroke_data:
            error_type = keystroke.get('error_type')
            if not error_type:
                continue
            
            error_count += 1
            
            if error_type not in patterns:
                patterns[error_type] = {
                    'count': 0,
                    'details': {}
                }
            
            patterns[error_type]['count'] += 1
            
            # Extract pattern details
            expected = keystroke.get('expected_character')
            actual = keystroke.get('character')
            
            if error_type == 'substitution' and expected and actual:
                pattern_key = f"{expected}->{actual}"
                patterns[error_type]['details'][pattern_key] = (
                    patterns[error_type]['details'].get(pattern_key, 0) + 1
                )
            elif error_type == 'insertion' and actual:
                patterns[error_type]['details'][actual] = (
                    patterns[error_type]['details'].get(actual, 0) + 1
                )
            elif error_type == 'deletion' and expected:
                patterns[error_type]['details'][expected] = (
                    patterns[error_type]['details'].get(expected, 0) + 1
                )
            elif error_type == 'transposition' and expected and actual:
                # For transposition, record the pair
                pair = f"{expected}{actual}"
                patterns[error_type]['details'][pair] = (
                    patterns[error_type]['details'].get(pair, 0) + 1
                )
        
        # Convert to ErrorPattern objects
        detected_patterns = []
        for error_type, data in patterns.items():
            total = data['count']
            percentage = (total / error_count * 100) if error_count > 0 else 0
            
            pattern = ErrorPattern(
                error_type=error_type,
                total_occurrences=total,
                percentage=round(percentage, 1),
                pattern_details=data['details'],
                under_pressure=is_high_speed,
                when_tired=is_late_session
            )
            detected_patterns.append(pattern)
        
        return detected_patterns

    def generate_coaching_insight(
        self,
        metrics: SkillMetrics,
        insight_type: InsightType
    ) -> Optional[Dict]:
        """
        Generate personalized, non-judgmental coaching insight.
        
        Creates feedback that makes user feel understood:
        - Celebrates strengths
        - Addresses weaknesses kindly
        - Highlights improvements
        - Suggests next steps
        
        Args:
            metrics: Calculated skill metrics
            insight_type: Type of insight to generate
            
        Returns:
            Dict with insight details or None if not applicable
        """
        insight = None
        
        if insight_type == InsightType.STRENGTH:
            insight = self._generate_strength_insight(metrics)
        elif insight_type == InsightType.WEAKNESS:
            insight = self._generate_weakness_insight(metrics)
        elif insight_type == InsightType.IMPROVEMENT:
            insight = self._generate_improvement_insight(metrics)
        elif insight_type == InsightType.PATTERN:
            insight = self._generate_pattern_insight(metrics)
        elif insight_type == InsightType.MILESTONE:
            insight = self._generate_milestone_insight(metrics)
        
        return insight

    def _generate_strength_insight(self, metrics: SkillMetrics) -> Optional[Dict]:
        """Generate insight about user strengths."""
        if metrics.avg_wpm < 40:
            return None
        
        return {
            'type': InsightType.STRENGTH.value,
            'tone': InsightTone.ENCOURAGING.value,
            'title': f"Strong WPM at {metrics.avg_wpm} words/min",
            'description': f"You're typing at a consistent {metrics.avg_wpm} WPM. That's solid foundation building.",
            'metric_name': 'wpm',
            'metric_value': metrics.avg_wpm,
            'priority': 7
        }

    def _generate_weakness_insight(self, metrics: SkillMetrics) -> Optional[Dict]:
        """Generate insight about areas for improvement."""
        if not metrics.weak_keys:
            return None
        
        worst_char = list(metrics.weak_keys.keys())[0]
        worst_stats = metrics.weak_keys[worst_char]
        error_rate = worst_stats['error_rate']
        
        return {
            'type': InsightType.WEAKNESS.value,
            'tone': InsightTone.HONEST.value,
            'title': f"'{worst_char}' needs some attention",
            'description': f"The '{worst_char}' key trips you up about {error_rate*100:.0f}% of the time. This is something we can improve together.",
            'recommendation': f"Try slow, intentional practice with '{worst_char}' in isolation. Speed comes after accuracy.",
            'metric_name': 'weak_key_error_rate',
            'metric_value': error_rate,
            'priority': 8
        }

    def _generate_improvement_insight(self, metrics: SkillMetrics) -> Optional[Dict]:
        """Generate insight about positive progress."""
        if metrics.improvement_week is None or metrics.improvement_week <= 0:
            return None
        
        return {
            'type': InsightType.IMPROVEMENT.value,
            'tone': InsightTone.CELEBRATORY.value,
            'title': f"You're getting faster! +{metrics.improvement_week:.1f}% this week",
            'description': f"Your WPM has improved by {metrics.improvement_week:.1f}% compared to last week. The practice is paying off.",
            'metric_name': 'improvement_week',
            'metric_value': metrics.improvement_week,
            'priority': 9
        }

    def _generate_pattern_insight(self, metrics: SkillMetrics) -> Optional[Dict]:
        """Generate insight about detected patterns."""
        error_patterns = metrics.error_patterns
        if not error_patterns:
            return None
        
        # Find most common error type
        most_common = max(error_patterns.items(), key=lambda x: x[1])
        error_type = most_common[0]
        count = most_common[1]
        
        patterns = {
            'substitution': 'You often hit the wrong key instead of the right one.',
            'insertion': 'Extra characters sometimes slip in—usually when you\'re going fast.',
            'deletion': 'You occasionally skip characters. Happens to everyone when focused.',
            'transposition': 'Adjacent keys sometimes swap places. Classic typo pattern.'
        }
        
        return {
            'type': InsightType.PATTERN.value,
            'tone': InsightTone.HONEST.value,
            'title': f"Your most common mistake: {error_type}",
            'description': f"{patterns.get(error_type, 'You have a typing pattern we can work on.')} This happens {count} times so far.",
            'metric_name': 'most_common_error',
            'metric_value': count,
            'priority': 6
        }

    def _generate_milestone_insight(self, metrics: SkillMetrics) -> Optional[Dict]:
        """Generate insight for milestones reached."""
        milestones = []
        
        if metrics.total_sessions >= 10:
            milestones.append({
                'title': '10 Sessions Complete!',
                'description': 'You\'ve built consistency. Keep this momentum going.',
                'priority': 9
            })
        
        if metrics.total_sessions >= 50:
            milestones.append({
                'title': '50 Sessions! You\'re Dedicated',
                'description': 'You\'ve typed tens of thousands of characters. Real improvement happens through commitment like this.',
                'priority': 10
            })
        
        if metrics.current_streak >= 5:
            milestones.append({
                'title': f'{metrics.current_streak} Perfect Sessions in a Row',
                'description': 'No errors for 5 sessions straight. That\'s the definition of flow state.',
                'priority': 10
            })
        
        if metrics.avg_accuracy >= 98:
            milestones.append({
                'title': 'Near-Perfect Accuracy',
                'description': '98%+ accuracy. You\'re typing like a pro.',
                'priority': 9
            })
        
        if milestones:
            milestone = milestones[0]  # Return first/best milestone
            return {
                'type': InsightType.MILESTONE.value,
                'tone': InsightTone.CELEBRATORY.value,
                'title': milestone['title'],
                'description': milestone['description'],
                'priority': milestone['priority']
            }
        
        return None
