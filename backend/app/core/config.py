# Purpose:
# This file loads and centralizes environment/configuration values used by the backend,
# such as database connection details, JWT settings, API secrets, and other runtime options.
#
# Why this file exists:
# Instead of hardcoding values in many different files, we keep all settings in one place.
# That makes the app easier to configure, safer to manage, and easier to move between
# local development, demo, and future production environments.

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "clinicsense")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "clinicsense")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "devpassword")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()