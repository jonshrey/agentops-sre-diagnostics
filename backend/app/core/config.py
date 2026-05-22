import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "AgentOps")
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    environment: str = os.getenv("ENVIRONMENT", "development")

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    cors_allow_origins: str = os.getenv("CORS_ALLOW_ORIGINS", "*")

    @property
    def llm_enabled(self) -> bool:
        return bool(self.gemini_api_key)


settings = Settings()