from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "IssueRadar AI"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: list[str] | str = ["http://localhost:3000", "http://localhost:5173"]

    FRONTEND_URL: str = "http://localhost:3000"

    DATABASE_URL: str = (
        "postgresql+asyncpg://issueradar:issueradar_secret_password@postgres:5432/issueradar_db"
    )
    REDIS_URL: str = "redis://redis:6379/0"

    # GitHub OAuth Configuration
    GITHUB_CLIENT_ID: str = "mock_github_client_id"
    GITHUB_CLIENT_SECRET: str = "mock_github_client_secret"
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"

    # Security Configuration
    JWT_SECRET_KEY: str = "dev_secret_jwt_key_issueradar_ai_at_least_32_chars_long"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days

    # Fernet key for encrypting GitHub tokens (32 url-safe base64-encoded bytes)
    ENCRYPTION_KEY: str = "xK9dJ_L2mN4pQ6rS8tV0wX2yZ4a6b8c0d2e4f6g8h0i="

    # AI Provider Settings
    AI_PROVIDER: str = "mock"  # mock | gemini | openai
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Redis & Celery Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Default Sync Interval
    SYNC_INTERVAL_DEFAULT: str = "24h"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
