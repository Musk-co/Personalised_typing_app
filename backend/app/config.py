"""
Configuration management for the application.
Supports environment-based config and easy adapter swapping.
"""

import os
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App metadata
    app_name: str = "Personalized Adaptive Typing Trainer"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, alias="DEBUG")

    # API Configuration
    api_prefix: str = "/api/v1"
    host: str = Field(default="0.0.0.0", alias="API_HOST")
    port: int = Field(default=8000, alias="API_PORT")

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./typing_trainer.db",
        alias="DATABASE_URL",
        description="SQLAlchemy database URL. Supports SQLite, PostgreSQL, etc.",
    )

    # Adapter Configuration (swappable)
    adapter_type: Literal["rule_based", "ml"] = Field(
        default="rule_based",
        alias="ADAPTER_TYPE",
        description="Typing adaptation strategy: 'rule_based' or 'ml'",
    )

    # Authentication
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        alias="SECRET_KEY",
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Feature Flags
    enable_real_time_feedback: bool = Field(
        default=True,
        alias="ENABLE_REAL_TIME_FEEDBACK",
    )
    enable_analytics: bool = Field(default=True, alias="ENABLE_ANALYTICS")
    enable_leaderboard: bool = Field(default=True, alias="ENABLE_LEADERBOARD")

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
