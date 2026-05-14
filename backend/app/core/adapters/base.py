"""
Abstract base adapter for typing training.
Defines the interface all adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class AdapterRecommendation:
    """Recommendation from an adapter."""

    next_difficulty: int  # 1-10
    focus_areas: List[str]  # Areas to focus on
    reason: str
    confidence: float  # 0-1


class BaseAdapter(ABC):
    """
    Abstract base class for typing adaptation engines.
    All adapters must implement this interface.
    """

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize adapter with optional configuration.
        
        Args:
            config: Dictionary of adapter-specific parameters
        """
        self.config = config or {}

    @abstractmethod
    def get_initial_difficulty(self, user_profile: dict) -> int:
        """
        Determine initial difficulty for new user.
        
        Args:
            user_profile: User data (experience, goals, etc.)
            
        Returns:
            Difficulty level 1-10
        """
        pass

    @abstractmethod
    def analyze_session(self, session_data: dict) -> dict:
        """
        Analyze a completed typing session.
        
        Args:
            session_data: {
                'wpm': float,
                'accuracy': float,
                'errors': int,
                'duration': int,
                'error_details': dict,
                'key_stats': dict,
                ...
            }
            
        Returns:
            Analysis results {
                'performance_level': str,
                'weak_areas': [str],
                'strong_areas': [str],
                ...
            }
        """
        pass

    @abstractmethod
    def recommend_next_difficulty(
        self,
        user_history: List[dict],
        current_performance: dict,
    ) -> AdapterRecommendation:
        """
        Recommend difficulty for next session.
        
        Args:
            user_history: List of past session summaries
            current_performance: Latest session analysis
            
        Returns:
            AdapterRecommendation with next difficulty and focus areas
        """
        pass

    @abstractmethod
    def get_real_time_feedback(self, current_stats: dict) -> Optional[str]:
        """
        Provide real-time feedback during a session.
        
        Args:
            current_stats: Current session metrics
            
        Returns:
            Feedback message or None
        """
        pass

    def validate_config(self) -> bool:
        """Validate adapter configuration."""
        return True

    def __repr__(self):
        return f"<{self.__class__.__name__}(config={self.config})>"
