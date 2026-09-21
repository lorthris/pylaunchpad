"""Application configuration settings for PyLaunchpad."""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for application runtime, security, and billing."""

    # Application settings
    APP_NAME: str = "PyLaunchpad"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security and authentication
    SECRET_KEY: str = Field(
        default="pylaunchpad_insecure_development_secret_key_replace_in_prod",
        description="Cryptographic secret key for signing JWT tokens and sessions",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./pylaunchpad.db",
        description="Database connection URL. SQLite default for zero-setup, PostgreSQL ready.",
    )

    # Polar.sh Merchant of Record billing
    POLAR_ACCESS_TOKEN: Optional[str] = None
    POLAR_ORGANIZATION_ID: Optional[str] = None
    POLAR_WEBHOOK_SECRET: Optional[str] = None
    POLAR_ENVIRONMENT: str = "sandbox"  # 'sandbox' or 'production'

    # CORS and security headers
    CORS_ORIGINS: List[str] = ["*"]

    # Rate limiting defaults
    DEFAULT_RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
