from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Stadium Operations AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    ALLOWED_HOSTS: List[str] = ["*"]

    # Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [h.strip() for h in v.split(",") if h.strip()]
        return v

settings = Settings()
