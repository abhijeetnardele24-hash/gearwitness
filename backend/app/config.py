import os
from enum import Enum

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppMode(str, Enum):
    FIXTURE = "fixture"
    LOCAL = "local"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "GearWitness"
    APP_VERSION: str = "0.1.0"
    APP_MODE: AppMode = AppMode.FIXTURE

    @field_validator("APP_MODE", mode="before")
    @classmethod
    def normalize_app_mode(cls, v):
        if isinstance(v, str):
            clean = v.strip().lower()
            if clean == "live":
                return AppMode.LOCAL
            return AppMode(clean)
        return v

    # Server
    HOST: str = "127.0.0.1"  # nosec B104
    PORT: int = 8000
    DATABASE_URL: str = "sqlite:///./gearwitness.db"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 15
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8000,http://127.0.0.1:5173,http://127.0.0.1:8000"

    # Open AI / Local Gemma Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    GEMMA_MODEL_NAME: str = "gemma3:4b"
    OLLAMA_MIN_VERSION: str = "0.6.0"
    MODEL_TIMEOUT_SECONDS: int = 45


_raw_mode = os.getenv("APP_MODE", "fixture").strip().lower()
if _raw_mode == "live":
    _raw_mode = "local"

settings = Settings(
    APP_MODE=AppMode(_raw_mode),
    HOST=os.getenv("HOST", "127.0.0.1"),
    OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    GEMMA_MODEL_NAME=os.getenv("GEMMA_MODEL_NAME", "gemma3:4b"),
    DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./gearwitness.db"),
    UPLOAD_DIR=os.getenv("UPLOAD_DIR", "./uploads"),
)
