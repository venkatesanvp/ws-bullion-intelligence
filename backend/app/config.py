from functools import lru_cache
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SCHEMA_REVISION = "0002_provider_ingestion"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)
    database_url: str
    local_app_token: SecretStr
    allowed_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    allowed_hosts: str = "127.0.0.1,localhost"
    max_import_bytes: int = Field(default=10 * 1024 * 1024, gt=0)
    max_import_rows: int = Field(default=100_000, gt=0)
    app_env: str = "development"
    # Step 5D.4 operating policy. Authentication settings remain separate/backend-only.
    market_data_enabled: bool = False
    market_data_auto_missing: bool = True
    market_data_max_requests: int = Field(default=8, ge=1, le=32)
    market_data_partition_days: int = Field(default=366, ge=1, le=366)
    market_data_timeout_seconds: int = Field(default=10, ge=1, le=30)
    market_data_freshness_seconds: int = Field(default=604800, ge=60, le=2592000)
    market_data_empty_retry_seconds: int = Field(default=3600, ge=60, le=86400)
    market_data_failure_backoff_seconds: int = Field(default=300, ge=60, le=86400)
    market_data_min_interval_seconds: float = Field(default=1, ge=0.2, le=60)
    market_data_daily_budget: int = Field(default=1000, ge=1, le=100000)
    market_data_max_rows: int = Field(default=100000, ge=1000, le=100000)
    market_data_max_coverage_days: int = Field(default=100000, ge=1000, le=200000)
    market_data_auto_refresh_seconds: int = Field(default=0, ge=0, le=86400)

    # Step 5E: independent capability switches under the standing read-only gate.
    market_quotes_enabled: bool = False
    market_intraday_enabled: bool = False
    market_quote_refresh_seconds: int = Field(default=15, ge=5, le=3600)
    market_quote_stale_seconds: int = Field(default=45, ge=15, le=3600)
    market_intraday_refresh_seconds: int = Field(default=60, ge=15, le=3600)
    market_intraday_partition_days: int = Field(default=7, ge=1, le=90)
    market_session_max_requests: int = Field(default=8, ge=1, le=16)
    market_session_max_rows: int = Field(default=100000, ge=1000, le=100000)
    market_provider_daily_budget: int = Field(default=10000, ge=100, le=100000)

    @field_validator("market_data_auto_refresh_seconds")
    @classmethod
    def refresh_interval(cls, value):
        if value and value < 60:
            raise ValueError("Automatic refresh must be disabled or at least 60 seconds")
        return value

    @field_validator("database_url")
    @classmethod
    def postgres_only(cls, value: str) -> str:
        if not value.startswith("postgresql+psycopg://"):
            raise ValueError("PostgreSQL psycopg URL required")
        return value

    @field_validator("local_app_token")
    @classmethod
    def strong_token(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < 32:
            raise ValueError("Use a locally generated token of at least 32 characters")
        return value

    @property
    def origins(self) -> list[str]:
        return [x.strip() for x in self.allowed_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
