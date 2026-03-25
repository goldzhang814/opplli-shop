from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_ENV:      Literal["development", "production"] = "development"
    APP_SECRET_KEY: str = "changeme"
    APP_NAME:     str   = "My Store"
    APP_URL:      str   = "http://localhost:9010"
    FRONTEND_URL: str   = "http://localhost:3000"
    ADMIN_URL:    str   = "http://localhost:3001"
    CORS_ORIGINS: str   = "http://localhost:3000,http://localhost:3001"

    # Database
    DATABASE_URL: str = "mysql+aiomysql://root:root@localhost:3306/ecom_db"

    # Redis
    REDIS_URL:      str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""

    # JWT
    JWT_SECRET_KEY:                  str = "changeme"
    JWT_ALGORITHM:                   str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # OAuth — Google
    GOOGLE_CLIENT_ID:     str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI:  str = ""

    # OAuth — Facebook
    FACEBOOK_CLIENT_ID:     str = ""
    FACEBOOK_CLIENT_SECRET: str = ""
    FACEBOOK_REDIRECT_URI:  str = ""

    # OAuth — Apple
    APPLE_CLIENT_ID:     str = ""
    APPLE_TEAM_ID:       str = ""
    APPLE_KEY_ID:        str = ""
    APPLE_PRIVATE_KEY:   str = ""
    APPLE_REDIRECT_URI:  str = ""

    # Payment — Stripe
    STRIPE_PUBLIC_KEY:      str = ""
    STRIPE_SECRET_KEY:      str = ""
    STRIPE_WEBHOOK_SECRET:  str = ""

    # Payment — PayPal
    PAYPAL_CLIENT_ID:     str = ""
    PAYPAL_CLIENT_SECRET: str = ""
    PAYPAL_MODE:          str = "sandbox"
    PAYPAL_WEBHOOK_ID:    str = ""

    # Payment — Airwallex
    AIRWALLEX_CLIENT_ID:      str = ""
    AIRWALLEX_API_KEY:        str = ""
    AIRWALLEX_WEBHOOK_SECRET: str = ""
    AIRWALLEX_ENV:            str = "demo"

    # Email
    EMAIL_PROVIDER:  str = "resend"
    EMAIL_FROM:      str = "noreply@example.com"
    EMAIL_FROM_NAME: str = "My Store"
    RESEND_API_KEY:  str = ""
    SENDGRID_API_KEY: str = ""
    SMTP_HOST:       str = ""
    SMTP_PORT:       int = 587
    SMTP_USER:       str = ""
    SMTP_PASSWORD:   str = ""

    # Storage
    STORAGE_BACKEND:    Literal["local", "s3"] = "local"
    #MEDIA_LOCAL_PATH:   str = "/app/media"
    MEDIA_LOCAL_PATH:   str = "./app/media"
    MEDIA_URL_PREFIX:   str = "/media"
    AWS_ACCESS_KEY_ID:  str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION:         str = "us-east-1"
    AWS_S3_BUCKET:      str = ""
    CLOUDFLARE_CDN_URL: str = ""

    # Super admin
    SUPER_ADMIN_EMAIL:    str = "admin@example.com"
    SUPER_ADMIN_PASSWORD: str = "changeme"

    # Celery
    CELERY_BROKER_URL:     str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
