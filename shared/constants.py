"""Shared types and constants for monorepo."""

# API Base URL (will be overridden in frontend config)
API_BASE_URL = "http://localhost:8000/api/v1"

# Test Types
TEST_TYPES = {
    "STANDARD": "standard",
    "CODING": "coding",
    "CUSTOM": "custom",
}

# Difficulty Levels
DIFFICULTY_LEVELS = {
    "BEGINNER": 1,
    "EASY": 2,
    "INTERMEDIATE": 3,
    "ADVANCED": 5,
    "EXPERT": 8,
    "EXTREME": 10,
}

# Performance Thresholds
THRESHOLDS = {
    "MIN_WPM": 20,
    "TARGET_ACCURACY": 85,
    "GOOD_WPM": 50,
}

# Adapter Types
ADAPTER_TYPES = {
    "RULE_BASED": "rule_based",
    "ML": "ml",
}
