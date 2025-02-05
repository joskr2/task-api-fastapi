import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Environment
    ENV: str = "development"

    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Database
    DATABASE_URL: str

    # OAuth2 settings and URLs
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_AUTH_URL: str
    GOOGLE_TOKEN_URL: str
    GOOGLE_USERINFO_URL: str

    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str
    GITHUB_AUTH_URL: str
    GITHUB_TOKEN_URL: str
    GITHUB_USERINFO_URL: str

    # CORS Settings
    CORS_ORIGINS: str
    CORS_METHODS: str
    CORS_HEADERS: str

    class Config:
        env_file = f".env.{os.getenv('ENV', 'development')}" if os.getenv('ENV') != 'production' else '.env'

settings = Settings()