# src/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "EthosMCP"
    PORT: int = 8000
    DATABASE_URL: str = "postgresql://user:password@host:port/dbname"
    CRYPTO_KEY: str = "supersecretkey"
    DATA_DIR: str = "./data"
    # Add other configuration variables as needed

settings = Settings()
