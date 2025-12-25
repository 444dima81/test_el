# app/core/config.py

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_KEY: str = "dev-key"

    FAISS_DIR: Path = Path("vectorize/store_faiss")
    HF_MODEL_NAME: str = "intfloat/multilingual-e5-large"

    GIGACHAT_API_KEY: str | None = None
    GIGACHAT_MODEL: str = "ai-sage/GigaChat3-10B-A1.8B"
    GIGACHAT_BASE_URL: str = "https://foundation-models.api.cloud.ru/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()