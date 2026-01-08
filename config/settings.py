from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.exceptions import ConfigurationError

COMMON_CONFIG = SettingsConfigDict(
    env_file=".env", env_file_encoding="utf-8", extra="ignore"
)


class DatabaseSettings(BaseSettings):
    user: str = Field(default="postgres", validation_alias="POSTGRES_USER")
    password: SecretStr = Field(
        default=SecretStr("postgres"), validation_alias="POSTGRES_PASSWORD"
    )
    db_name: str = Field(default="qa_orchestrator_db", validation_alias="POSTGRES_DB")
    host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    port: int = Field(default=5432, validation_alias="POSTGRES_PORT")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        """
        Constructs the SQLAlchemy database URL.
        Format: postgresql://user:password@host:port/dbname
        """
        return (
            f"postgresql://{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.db_name}"
        )

    model_config = COMMON_CONFIG


class BookerSettings(BaseSettings):
    username: str = Field(..., validation_alias="BOOKER_USERNAME")
    password: str = Field(..., validation_alias="BOOKER_PASSWORD")

    model_config = COMMON_CONFIG


class Settings(BaseSettings):
    app_env: Literal["dev", "test", "prod"] = Field(default="dev")
    base_url: AnyHttpUrl = Field(..., description="Base URL for the target API")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )

    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    booker: BookerSettings = Field(default_factory=BookerSettings)  # type: ignore[arg-type]

    model_config = COMMON_CONFIG


try:
    # Mypy cannot see that pydantic-settings injects values from .env,
    settings = Settings()  # type: ignore[call-arg]
except Exception as e:
    raise ConfigurationError(f"Failed to load configuration: {e}") from e
