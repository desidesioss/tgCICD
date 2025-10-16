"""Application configuration loaded via Pydantic BaseSettings."""
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Holds runtime configuration derived from environment variables."""

    bot_token: str = Field(..., env="TG_TOKEN")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_settings() -> Settings:
    """Load settings from environment or .env and fail fast when missing."""
    try:
        return Settings()
    except ValidationError as exc:  # pragma: no cover - defensive, hard to trigger
        raise RuntimeError(
            "Bot token is not configured. "
            "Set TG_TOKEN in the environment or in an .env file.",
        ) from exc
