from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Booking App"
    database_url: str
    test_database_url: str = (
        "postgresql://postgres:postgres@localhost:5432/booking_app_test"
    )
    port: int

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
