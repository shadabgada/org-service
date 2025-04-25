from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # Database configuration
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()