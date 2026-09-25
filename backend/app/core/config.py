from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str
    gemini_chat_model: str = "gemini-3.6-flash"
    gemini_fallback_model: str = "gemini-2.5-flash"
    gemini_embed_model: str = "gemini-embedding-2"
    frontend_url: str = "http://localhost:4200"
    top_k: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 150
    max_file_size_mb: int = 5
    index_path: str = "data/vector_index.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
