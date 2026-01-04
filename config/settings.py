from typing import Literal

from pydantic import AnyHttpUrl, Field
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
