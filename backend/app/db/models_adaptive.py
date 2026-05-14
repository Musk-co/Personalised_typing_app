"""
Additional models for adaptive training and exercise generation.
Appended to models.py
"""

# Add to the end of models.py:

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
