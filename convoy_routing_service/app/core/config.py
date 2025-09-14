from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Field names are now lowercase to match environment variable mapping
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"

settings = Settings()