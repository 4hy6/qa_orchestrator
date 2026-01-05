from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.exceptions import ConfigurationError


class Settings(BaseSettings):
    app_env: Literal["dev", "test", "prod"] = Field(default="dev")
    base_url: AnyHttpUrl = Field(..., description="Base URL for the target API")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )

    booker_username: str = Field(description="Username for Booker API")
    booker_password: str = Field(description="Password for Booker API")

    # Database Settings
    postgres_user: str = Field(default="postgres")
    postgres_password: SecretStr = Field(default=SecretStr("postgres"))
    postgres_db: str = Field(default="qa_orchestrator_db")
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """
        Constructs the SQLAlchemy database URL.
        Format: postgresql://user:password@host:port/dbname
        """
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password.get_secret_value()}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


try:
    # Mypy cannot see that pydantic-settings injects values from .env,
    settings = Settings()  # type: ignore[call-arg]
except Exception as e:
    raise ConfigurationError(f"Failed to load configuration: {e}") from e
