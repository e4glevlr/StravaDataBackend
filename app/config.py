# app/config.py
from pydantic import BaseSettings


class Settings(BaseSettings):
    # Cài đặt ứng dụng
    SECRET_KEY: str = "YOUR_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Cài đặt Email
    EMAIL_FROM: str = "your-email@example.com"
    EMAIL_USERNAME: str = "your-email@example.com"
    EMAIL_PASSWORD: str = "your-email-password"
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    # Cài đặt Strava
    STRAVA_CLIENT_ID: str = ""
    STRAVA_CLIENT_SECRET: str = ""
    STRAVA_REDIRECT_URI = "http://localhost:8000"


    class Config:
        env_file = ".env"


settings = Settings()