from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_safe_browsing_api_key: str | None = None
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_image_bytes: int = 5 * 1024 * 1024
    max_image_pixels: int = 20_000_000
    request_timeout_seconds: float = 8.0
    rdap_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
