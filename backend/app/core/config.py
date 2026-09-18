"""Application configuration.

Configuration is environment-driven so the same application can run with
PostgreSQL locally and DynamoDB/S3/Bedrock on AWS without changing domain
logic.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import (
    APP_NAME,
    Environment,
    StorageBackend,
)


class Settings(BaseSettings):
    """Runtime configuration for AgentTrace."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = APP_NAME
    app_env: Environment = Environment.LOCAL
    debug: bool = False
    log_level: str = "INFO"

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    api_v1_prefix: str = "/api/v1"

    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/agenttrace"
    )

    storage_backend: StorageBackend = StorageBackend.POSTGRES

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    auth_enabled: bool = False

    jwt_secret_key: str = "development-only-change-this-secret"
    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # ------------------------------------------------------------------
    # AWS
    # ------------------------------------------------------------------

    aws_region: str = "ap-south-1"

    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_session_token: str | None = None

    dynamodb_table: str = "agenttrace"
    s3_bucket: str | None = None

    # Bedrock is optional.
    bedrock_model_id: str | None = None

    # ------------------------------------------------------------------
    # AWS runtime
    # ------------------------------------------------------------------

    aws_endpoint_url: str | None = None

    # ------------------------------------------------------------------
    # Application behavior
    # ------------------------------------------------------------------

    enable_demo_mode: bool = True
    enable_bedrock: bool = False

    # Maximum size accepted for one telemetry request in bytes.
    max_telemetry_payload_bytes: int = 1_000_000

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        """Normalize log-level configuration."""

        normalized = value.strip().upper()

        valid_levels = {
            "CRITICAL",
            "ERROR",
            "WARNING",
            "INFO",
            "DEBUG",
        }

        if normalized not in valid_levels:
            raise ValueError(
                f"Invalid LOG_LEVEL '{value}'. "
                f"Expected one of: {', '.join(sorted(valid_levels))}."
            )

        return normalized

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        """Accept either a JSON-like list or comma-separated origins."""

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return []

            if value.startswith("[") and value.endswith("]"):
                import json

                parsed = json.loads(value)

                if not isinstance(parsed, list):
                    raise ValueError("CORS_ALLOWED_ORIGINS must be a list.")

                return [str(origin).strip() for origin in parsed if str(origin).strip()]

            return [
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            ]

        if isinstance(value, (list, tuple, set)):
            return [str(origin).strip() for origin in value if str(origin).strip()]

        raise ValueError(
            "CORS_ALLOWED_ORIGINS must be a list or comma-separated string."
        )

    @property
    def is_local(self) -> bool:
        """Whether the application is running locally."""

        return self.app_env in {
            Environment.LOCAL,
            Environment.TEST,
        }

    @property
    def is_aws(self) -> bool:
        """Whether AWS-backed infrastructure is configured."""

        return self.app_env == Environment.AWS

    @property
    def sqlalchemy_database_url(self) -> str:
        """Return the configured async SQLAlchemy database URL."""

        return self.database_url

    def validate_production_configuration(self) -> None:
        """Validate configuration that must be safe in AWS/production.

        This is deliberately explicit rather than running automatically during
        import. That keeps local development and test configuration simple.
        """

        if self.auth_enabled and self.jwt_secret_key == (
            "development-only-change-this-secret"
        ):
            raise ValueError(
                "JWT_SECRET_KEY must be changed when AUTH_ENABLED=true."
            )

        if "*" in self.cors_allowed_origins:
            raise ValueError(
                "Wildcard CORS is not permitted when authentication is enabled."
            )

        if self.is_aws and not self.dynamodb_table:
            raise ValueError("DYNAMODB_TABLE is required for AWS deployment.")

        if self.is_aws and not self.s3_bucket:
            raise ValueError("S3_BUCKET is required for AWS deployment.")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""

    return Settings()


settings = get_settings()