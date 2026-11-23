from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_ENV: str = "production"
    APP_DEBUG: bool = False

    # Either pass a full DATABASE_URL, or the separate DB_* parts.
    # In the cloud the password comes from Secrets Manager as DB_PASSWORD.
    DATABASE_URL: str | None = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "travel_planner"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""

    ARTIC_API_ENABLED: bool = True
    ARTIC_API_BASE_URL: str = "https://api.artic.edu/api/v1"
    ARTIC_API_TIMEOUT: int = 10

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
