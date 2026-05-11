from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    debug: bool = False
    db_url: PostgresDsn = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/app"
    )
    db_echo: bool = False
    db_pool_size: int = 20
    db_max_overflow: int = 10
    secret_key: str
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = ["*"]


settings = Settings()
