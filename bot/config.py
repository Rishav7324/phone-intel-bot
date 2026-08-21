"""Configuration management for Telegram Phone Number Intelligence Bot."""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Telegram Bot Token from @BotFather
    bot_token: str = Field(default="", validation_alias="BOT_TOKEN")

    # Admin User IDs for /stats access (can be single int, comma-separated string, or list)
    admin_id: Optional[str] = Field(default=None, validation_alias="ADMIN_ID")
    admin_ids: List[int] = Field(default_factory=list)

    # SQLite Database File Path
    database_path: str = Field(default="bot.db", validation_alias="DATABASE_PATH")

    # Optional default country code fallback (e.g., 'IN', 'US', 'GB')
    default_region: Optional[str] = Field(default=None, validation_alias="DEFAULT_REGION")

    # Rate Limiting: lookups allowed per user per minute
    rate_limit_per_minute: int = Field(default=10, validation_alias="RATE_LIMIT_PER_MINUTE")

    # Cache TTL for number lookups (seconds)
    cache_ttl_seconds: int = Field(default=600, validation_alias="CACHE_TTL_SECONDS")

    # Logging level
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # Runtime environment
    environment: str = Field(default="production", validation_alias="ENVIRONMENT")

    @field_validator("default_region", mode="before")
    @classmethod
    def clean_default_region(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize default region string."""
        if not v or not isinstance(v, str) or not v.strip():
            return None
        cleaned = v.strip().upper()
        return cleaned if len(cleaned) == 2 else None

    @field_validator("admin_ids", mode="before")
    @classmethod
    def assemble_admin_ids(cls, v: Optional[List[int]], info) -> List[int]:
        """Convert ADMIN_ID environment variable into a list of integer IDs."""
        if isinstance(v, list) and v:
            return v

        admin_id_val = info.data.get("admin_id") if info.data else None
        if not admin_id_val:
            return []

        ids: List[int] = []
        for raw_id in str(admin_id_val).split(","):
            raw_id = raw_id.strip()
            if raw_id.isdigit():
                ids.append(int(raw_id))
        return ids

    def is_admin(self, user_id: int) -> bool:
        """Check if a given Telegram user ID is an authorized admin."""
        return user_id in self.admin_ids


@lru_cache()
def get_settings() -> Settings:
    """Return cached singleton instance of application settings."""
    return Settings()
