"""
SQLAlchemy models for the application.
Designed for extensibility and future analytics/ML.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sessions = relationship("TypingSession", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    adapter_config = relationship("UserAdapterConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class UserPreference(Base):
    """User preferences and settings."""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    theme = Column(String(20), default="light")  # light, dark, auto
    notifications_enabled = Column(Boolean, default=True)
    language = Column(String(10), default="en")
    keyboard_layout = Column(String(20), default="qwerty")
    sound_enabled = Column(Boolean, default=True)
    difficulty_auto_adjust = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_settings = Column(JSON, default=dict)  # For extensibility

    # Relationships
    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id})>"


class UserAdapterConfig(Base):
    """User's adapter configuration and preferences."""

    __tablename__ = "user_adapter_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    adapter_type = Column(String(50), default="rule_based")  # rule_based, ml, etc.
    parameters = Column(JSON, default=dict)  # Adapter-specific parameters
    custom_rules = Column(JSON, default=dict)  # Custom rules for rule-based adapter
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="adapter_config")

    def __repr__(self):
        return f"<UserAdapterConfig(user_id={self.user_id}, adapter_type={self.adapter_type})>"


class TypingSession(Base):
    """A typing test session with comprehensive metrics."""

    __tablename__ = "typing_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    test_type = Column(String(50), default="standard")  # standard, coding, custom, etc.
    difficulty_level = Column(Integer, default=1)  # 1-10
    status = Column(String(20), default="in_progress")  # in_progress, completed, paused
    
    # Text data
    text_prompt = Column(Text)  # The text the user typed
    text_typed = Column(Text)  # What the user actually typed
    custom_text = Column(Boolean, default=False)  # Was this custom text?

    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Core metrics
    wpm = Column(Float, nullable=True)  # Words per minute
    accuracy = Column(Float, nullable=True)  # Accuracy percentage (0-100)
    errors = Column(Integer, default=0)  # Total errors
    key_presses = Column(Integer, default=0)  # Total key presses

    # Detailed error tracking (for analysis)
    error_details = Column(JSON, default=dict)  # {position: {expected, actual}, ...}
    key_stats = Column(JSON, default=dict)  # Per-key statistics for ML

    # Adapter-specific data
    adapter_used = Column(String(50), nullable=True)  # Which adapter was active
    adapter_recommendation = Column(JSON, nullable=True)  # Recommendation received

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<TypingSession(id={self.id}, user_id={self.user_id}, wpm={self.wpm})>"


class SessionMetric(Base):
    """Granular metrics for real-time tracking within a session."""

    __tablename__ = "session_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("typing_sessions.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Real-time metrics
    current_wpm = Column(Float)
    current_accuracy = Column(Float)
    errors_so_far = Column(Integer)
    characters_typed = Column(Integer)
    
    # Additional context
    adapter_state = Column(JSON, nullable=True)  # Adapter state at this point
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SessionMetric(session_id={self.session_id}, timestamp={self.timestamp})>"


class UserStatSnapshot(Base):
    """Periodic snapshots of user statistics for fast analytics."""

    __tablename__ = "user_stat_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Aggregated stats
    total_sessions = Column(Integer, default=0)
    avg_wpm = Column(Float, nullable=True)
    best_wpm = Column(Float, nullable=True)
    avg_accuracy = Column(Float, nullable=True)
    total_errors = Column(Integer, default=0)
    total_practice_hours = Column(Float, default=0)
    
    # Trends
    weekly_improvement = Column(Float, nullable=True)  # % improvement week over week
    monthly_improvement = Column(Float, nullable=True)
    
    # Ranking
    rank = Column(Integer, nullable=True)
    percentile = Column(Float, nullable=True)
    
    # Time period
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UserStatSnapshot(user_id={self.user_id}, avg_wpm={self.avg_wpm})>"


class Keystroke(Base):
    """Individual keystroke events with error classification."""

    __tablename__ = "keystrokes"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("typing_sessions.id"), nullable=False, index=True)
    
    # Keystroke data
    character = Column(String(1), nullable=False)  # Character typed
    expected_character = Column(String(1), nullable=True)  # Expected character at position
    position = Column(Integer, nullable=False)  # Position in text
    
    # Timing
    timestamp_ms = Column(Float, nullable=False)  # Timestamp in milliseconds
    
    # Correctness
    is_correct = Column(Boolean, default=False)  # Whether keystroke is correct
    error_type = Column(
        String(50), 
        nullable=True
    )  # insertion, deletion, substitution, transposition
    
    # Context
    context = Column(String(255), nullable=True)  # Additional context
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Keystroke(session_id={self.session_id}, position={self.position}, char={self.character}, error_type={self.error_type})>"


class UserSkillProfile(Base):
    """
    Aggregated user skill profile.
    
    This is the "heart" of personalization - a dynamic profile that evolves with every session.
    Captures current aggregated metrics, weak keys, and error patterns that make the user feel known.
    """

    __tablename__ = "user_skill_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # Overall Performance (Rolling Averages)
    avg_wpm = Column(Float, default=0.0)  # Current rolling average WPM
    avg_accuracy = Column(Float, default=0.0)  # Current rolling average accuracy (0-100)
    total_sessions = Column(Integer, default=0)  # Total sessions completed
    total_keystrokes = Column(Integer, default=0)  # Total keystrokes captured
    total_errors = Column(Integer, default=0)  # Total errors across all sessions
    
    # Performance Trends
    improvement_week = Column(Float, nullable=True)  # Week-over-week WPM change
    improvement_month = Column(Float, nullable=True)  # Month-over-month WPM change
    consistency_score = Column(Float, default=0.0)  # How consistent is performance (0-100)
    
    # Weak Keys Summary (JSON: {char: {frequency, error_rate}})
    weak_keys = Column(JSON, default=dict)  # Most problematic characters
    # Example: {"a": {"frequency": 25, "error_rate": 0.24}, "s": {"frequency": 15, "error_rate": 0.13}}
    
    # Error Pattern Summary (JSON: {type: count})
    error_patterns = Column(JSON, default=dict)  # Common mistakes
    # Example: {"substitution": 145, "insertion": 89, "deletion": 32, "transposition": 18}
    
    # Personal Stats (for personalization feeling)
    best_wpm = Column(Float, nullable=True)  # Best WPM achieved
    best_accuracy = Column(Float, nullable=True)  # Best accuracy achieved
    longest_streak = Column(Integer, default=0)  # Sessions without mistakes
    current_streak = Column(Integer, default=0)  # Current error-free sessions
    
    # Metadata
    profile_version = Column(Integer, default=1)  # Version for migration purposes
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UserSkillProfile(user_id={self.user_id}, avg_wpm={self.avg_wpm:.1f}, avg_accuracy={self.avg_accuracy:.1f})>"


class SkillSnapshot(Base):
    """
    Time-series snapshots of user skill profile.
    
    Captured periodically (e.g., after each session or daily) to track progress over time.
    Enables "where was I 2 weeks ago vs. now" insights.
    """

    __tablename__ = "skill_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Session context
    session_id = Column(Integer, ForeignKey("typing_sessions.id"), nullable=True)
    
    # Performance snapshot
    wpm = Column(Float)  # WPM at this point
    accuracy = Column(Float)  # Accuracy at this point
    total_sessions = Column(Integer)  # Total sessions up to this point
    
    # Cumulative stats
    cumulative_wpm_avg = Column(Float)  # Running average
    cumulative_accuracy_avg = Column(Float)  # Running average
    cumulative_errors = Column(Integer)  # Total errors
    
    # Weak keys at this point (JSON)
    weak_keys_snapshot = Column(JSON, default=dict)  # Weak key state
    
    # Error pattern at this point (JSON)
    error_pattern_snapshot = Column(JSON, default=dict)  # Error pattern state
    
    # Trend data
    wpm_change = Column(Float, nullable=True)  # Change since last snapshot
    accuracy_change = Column(Float, nullable=True)  # Change since last snapshot
    
    # Metadata
    snapshot_date = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SkillSnapshot(user_id={self.user_id}, wpm={self.wpm:.1f}, accuracy={self.accuracy:.1f})>"


class WeakKeyProfile(Base):
    """
    Detailed profile of each character the user types.
    
    Tracks:
    - How often they hit each key
    - What percentage they get wrong
    - Which types of errors are common for that key
    - Recovery patterns (how long to fix mistakes)
    """

    __tablename__ = "weak_key_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    character = Column(String(1), nullable=False)  # The character being tracked
    
    # Frequency
    total_attempts = Column(Integer, default=0)  # How many times typed
    total_errors = Column(Integer, default=0)  # How many times wrong
    
    # Error rate and type distribution
    error_rate = Column(Float, default=0.0)  # error_count / attempts
    error_distribution = Column(JSON, default=dict)
    # Example: {"substitution": 15, "insertion": 5, "deletion": 3}
    
    # Performance indicators
    avg_keystroke_time = Column(Float, nullable=True)  # Average time to type this key
    error_keystroke_time = Column(Float, nullable=True)  # Time when errors happen
    
    # Recent context (last N sessions)
    recent_attempts = Column(Integer, default=0)  # Attempts in last 5 sessions
    recent_errors = Column(Integer, default=0)  # Errors in last 5 sessions
    recent_error_rate = Column(Float, default=0.0)  # Recent error rate
    
    # Trend
    trend = Column(String(20), default="stable")  # improving, stable, declining
    improvement_pct = Column(Float, nullable=True)  # Improvement since first session
    
    # Metadata
    first_seen = Column(DateTime, default=datetime.utcnow)  # When user first typed this
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WeakKeyProfile(user_id={self.user_id}, char='{self.character}', error_rate={self.error_rate:.2%})>"


class ErrorPatternProfile(Base):
    """
    Detailed profile of user's error patterns.
    
    Tracks:
    - Substitution patterns (what char mistakes happen for each key)
    - Insertion habits (what extras get typed)
    - Deletion patterns (what gets skipped)
    - Transposition tendencies (which adjacent chars swap)
    """

    __tablename__ = "error_pattern_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    error_type = Column(
        String(50), 
        nullable=False
    )  # substitution, insertion, deletion, transposition
    
    # Frequency
    total_occurrences = Column(Integer, default=0)  # How many times this error happens
    percentage = Column(Float, default=0.0)  # Of all errors
    
    # Pattern details (JSON - varies by error type)
    pattern_details = Column(JSON, default=dict)
    # For substitution: {"a->s": 15, "e->3": 8, ...}
    # For insertion: {"a": 12, "e": 8, ...} (what gets inserted)
    # For deletion: {"a": 10, "e": 7, ...} (what gets skipped)
    # For transposition: {"ae": 5, "rs": 3, ...} (pairs that swap)
    
    # Context analysis
    appears_under_pressure = Column(Boolean, default=False)  # More at high speeds?
    appears_when_tired = Column(Boolean, default=False)  # Later in session?
    appears_in_difficult_text = Column(Boolean, default=False)  # Pattern-specific?
    
    # Metadata
    first_observed = Column(DateTime, default=datetime.utcnow)
    last_observed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sessions_with_error = Column(Integer, default=0)  # How many sessions had this

    def __repr__(self):
        return f"<ErrorPatternProfile(user_id={self.user_id}, error_type={self.error_type}, occurrences={self.total_occurrences})>"


class UserSkillInsight(Base):
    """
    Coaching insights generated from user's skill profile.
    
    Non-judgmental, personalized feedback that makes the user feel understood.
    Updated regularly, builds narrative over time.
    """

    __tablename__ = "user_skill_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Insight details
    insight_type = Column(
        String(50),
        nullable=False
    )  # strength, weakness, improvement, pattern, milestone
    title = Column(String(200), nullable=False)  # Brief insight title
    description = Column(Text, nullable=False)  # Detailed insight
    
    # Data-driven
    metric_name = Column(String(100), nullable=True)  # What metric this is about
    metric_value = Column(Float, nullable=True)  # Current value
    benchmark = Column(Float, nullable=True)  # Average for reference
    
    # Actionability
    recommendation = Column(Text, nullable=True)  # What user should do
    recommended_difficulty = Column(Integer, nullable=True)  # Suggested difficulty level
    
    # Tone (for personalization)
    tone = Column(String(50), default="encouraging")  # encouraging, cautionary, celebratory, honest
    
    # Status
    is_active = Column(Boolean, default=True)  # Still relevant?
    priority = Column(Integer, default=5)  # 1-10, importance
    
    # Temporal
    observed_since = Column(DateTime, nullable=True)  # When pattern first noticed
    last_seen = Column(DateTime, default=datetime.utcnow)  # When last relevant
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UserSkillInsight(user_id={self.user_id}, type={self.insight_type}, title='{self.title[:30]}...')>"


class Exercise(Base):
    """
    Generated exercise for user training.
    
    Each exercise is freshly generated from user's skill data.
    Never static - always tailored to current weaknesses.
    """

    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Exercise content
    text_prompt = Column(Text, nullable=False)  # The text to type
    exercise_type = Column(String(50), nullable=False)  # weak_key_drill, error_pattern, mixed, etc.
    difficulty = Column(Integer, default=5)  # 1-10
    
    # Focus areas
    focus_chars = Column(JSON, default=list)  # Characters this exercise targets
    # Example: ["s", "p", ","]
    
    # Metadata
    description = Column(Text)  # Human-readable description
    expected_duration_seconds = Column(Integer, default=60)
    exercise_metadata = Column(JSON, default=dict)  # Additional context
    # Example: {"focus_weight": 0.6, "error_rates": {"s": 0.24}, "includes_punctuation": true}
    
    # Status
    is_active = Column(Boolean, default=True)  # User can still attempt
    was_attempted = Column(Boolean, default=False)  # Has user attempted?
    attempt_count = Column(Integer, default=0)  # How many times attempted
    
    # Temporal
    generated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # When this exercise becomes stale
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Exercise(user_id={self.user_id}, type={self.exercise_type}, difficulty={self.difficulty})>"


class ExerciseAttempt(Base):
    """
    Record of user attempting an exercise.
    
    Captures performance and feeds back into skill model.
    """

    __tablename__ = "exercise_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("typing_sessions.id"), nullable=True)
    
    # Performance
    accuracy = Column(Float)  # User's accuracy on this exercise
    wpm = Column(Float)  # User's WPM on this exercise
    errors = Column(Integer, default=0)  # Total errors
    
    # Time
    duration_seconds = Column(Integer)  # Actual time taken
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Feedback
    difficulty_felt = Column(String(50), nullable=True)  # easy, fair, hard, too_hard
    confidence_level = Column(Integer, nullable=True)  # 1-10, how confident user felt
    
    # Metadata
    was_successful = Column(Boolean, default=False)  # Did user "pass"?
    adaptation_applied = Column(String(50), nullable=True)  # maintain, increase, decrease
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ExerciseAttempt(user_id={self.user_id}, accuracy={self.accuracy:.1f}%, wpm={self.wpm:.1f})>"


class PlacementTest(Base):
    """
    Record of placement test taken by user.
    
    Used to classify initial skill level and set starting difficulty.
    """

    __tablename__ = "placement_tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Test structure (three parts: easy, medium, hard)
    easy_accuracy = Column(Float, nullable=True)  # Easy section accuracy
    easy_wpm = Column(Float, nullable=True)
    easy_duration = Column(Integer, nullable=True)
    
    medium_accuracy = Column(Float, nullable=True)  # Medium section accuracy
    medium_wpm = Column(Float, nullable=True)
    medium_duration = Column(Integer, nullable=True)
    
    hard_accuracy = Column(Float, nullable=True)  # Hard section accuracy
    hard_wpm = Column(Float, nullable=True)
    hard_duration = Column(Integer, nullable=True)
    
    # Results
    classified_level = Column(String(50), nullable=True)  # beginner, intermediate, advanced
    recommended_difficulty = Column(Integer, nullable=True)  # Starting difficulty
    confidence = Column(Float, nullable=True)  # 0-1, confidence in classification
    
    # Metadata
    test_duration_seconds = Column(Integer)  # Total time for all three sections
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PlacementTest(user_id={self.user_id}, level={self.classified_level})>"


class AdaptationRule(Base):
    """
    Configuration for adaptation engine thresholds.
    
    Allows fine-tuning of difficulty adjustment rules without code changes.
    """

    __tablename__ = "adaptation_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # None = system-wide
    
    # Rule definition
    rule_name = Column(String(100), nullable=False)  # e.g., "accuracy_too_low"
    rule_type = Column(String(50), nullable=False)  # threshold, range, etc.
    
    # Thresholds
    condition = Column(String(50), nullable=False)  # accuracy_below, accuracy_above, wpm_above, etc.
    threshold_value = Column(Float, nullable=False)  # The threshold
    
    # Action
    action = Column(String(50), nullable=False)  # increase, decrease, maintain
    action_value = Column(Integer, nullable=True)  # Amount to change (e.g., +1, -2)
    
    # Additional context
    priority = Column(Integer, default=5)  # Rule priority (higher = evaluated first)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AdaptationRule(name={self.rule_name}, condition={self.condition}>{self.threshold_value})>"


class Achievement(Base):
    """
    User achievements and badges.
    
    Celebrates milestones and encourages continued practice.
    """

    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Achievement metadata
    achievement_type = Column(String(100), nullable=False)  # perfect_session, speed_demon, accuracy_master, etc.
    title = Column(String(200), nullable=False)  # "Speedster" 
    description = Column(Text)  # What this achievement represents
    icon = Column(String(50), nullable=True)  # Icon name or emoji
    
    # Rarity (for pride factor)
    rarity = Column(String(50), default="common")  # common, rare, epic, legendary
    
    # Progress tracking
    progress_value = Column(Float, nullable=True)  # Value that triggered achievement (e.g., 75 WPM)
    requirement = Column(String(200), nullable=True)  # What was required (e.g., "75 WPM")
    
    # Metadata
    earned_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Achievement(user_id={self.user_id}, type={self.achievement_type})>"


class UserStreak(Base):
    """
    Tracks practice streaks and consistency.
    
    Motivates users to practice regularly.
    """

    __tablename__ = "user_streaks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Streak data
    streak_type = Column(String(50), nullable=False)  # days_practiced, sessions, error_free
    current_count = Column(Integer, default=0)  # Current streak length
    longest_count = Column(Integer, default=0)  # Personal best
    
    # Tracking
    last_activity_date = Column(DateTime, nullable=True)  # When streak was last extended
    started_at = Column(DateTime, default=datetime.utcnow)  # When current streak started
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserStreak(user_id={self.user_id}, type={self.streak_type}, current={self.current_count})>"


class Milestone(Base):
    """
    Significant achievements and personal records.
    
    Marks meaningful progress moments.
    """

    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Milestone details
    milestone_type = Column(String(100), nullable=False)  # first_50_wpm, 95_accuracy, no_errors, etc.
    title = Column(String(200), nullable=False)  # "First 50 WPM!"
    description = Column(Text)  # Celebratory message
    
    # Value achieved
    metric_name = Column(String(100), nullable=True)  # WPM, accuracy, session_count, etc.
    metric_value = Column(Float, nullable=True)  # The value achieved (e.g., 50.5)
    
    # Context
    session_id = Column(Integer, ForeignKey("typing_sessions.id"), nullable=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=True)
    
    # Status
    celebration_shown = Column(Boolean, default=False)  # Has user seen the celebration?
    
    # Metadata
    achieved_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Milestone(user_id={self.user_id}, type={self.milestone_type}, value={self.metric_value})>"


class ProgressSnapshot(Base):
    """
    Periodic snapshots for trend visualization.
    
    Captures overall progress metrics at regular intervals (daily).
    Enables "I'm actually getting better" visualizations.
    """

    __tablename__ = "progress_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Performance metrics
    avg_wpm = Column(Float)  # Average WPM at this point
    avg_accuracy = Column(Float)  # Average accuracy at this point
    best_wpm = Column(Float, nullable=True)  # Best WPM recorded so far
    best_accuracy = Column(Float, nullable=True)  # Best accuracy recorded so far
    
    # Volume metrics
    total_sessions = Column(Integer, default=0)  # Total sessions up to this point
    total_practice_minutes = Column(Float, default=0)  # Total practice time
    total_keystrokes = Column(Integer, default=0)  # Total keys typed
    total_errors = Column(Integer, default=0)  # Total errors
    
    # Keyboard heatmap
    keyboard_heatmap = Column(JSON, default=dict)  # {char: error_rate} for visualization
    
    # Weak keys at this moment
    weak_keys_at_time = Column(JSON, default=list)  # Top 5 weak keys
    
    # Trend indicators
    week_improvement_pct = Column(Float, nullable=True)  # % improvement this week
    month_improvement_pct = Column(Float, nullable=True)  # % improvement this month
    
    # Metadata
    snapshot_date = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProgressSnapshot(user_id={self.user_id}, wpm={self.avg_wpm:.1f}, accuracy={self.avg_accuracy:.1f})>"