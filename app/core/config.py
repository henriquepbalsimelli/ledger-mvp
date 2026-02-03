# app/core/config.py
import os
from pydantic_settings import BaseSettings

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str

    log_level: str = "INFO"
    service_name: str = "ledger-api"
    environment: str = "local"

    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False

settings = Settings()