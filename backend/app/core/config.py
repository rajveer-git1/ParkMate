import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings:
    app_name: str = "ParkMate API"
    database_url: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{(BASE_DIR / 'parkmate.db').as_posix()}"
    )
    secret_key: str = os.getenv("SECRET_KEY", "dev-only-change-this-secret-key")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()