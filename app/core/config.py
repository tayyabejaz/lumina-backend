"""Typed settings (12-factor). Single source of config; injected, never imported ad hoc (SOLID: DIP)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    port: int = 8000
    database_url: str
    database_replica_url: str | None = None
    redis_url: str = "redis://localhost:6379"
    queue_redis_url: str = "redis://localhost:6379/1"
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    supabase_jwt_secret: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # import this singleton
