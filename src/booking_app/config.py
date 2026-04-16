from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    app_name: str = "Booking App"
    app_env: str
    debug: bool = False
    database_url: str
    test_database_url: str
    secret_key: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @field_validator("app_env")
    @classmethod
    def validate_env(cls, v):
        allowed = {"development", "production", "test"}
        if v not in allowed:
            raise ValueError(f"Invalid app_env: {v}")
        return v


settings = Settings()
