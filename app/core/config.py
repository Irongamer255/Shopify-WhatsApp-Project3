from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Shopify WhatsApp Integration"
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "root"
    POSTGRES_PASSWORD: str = "" # Update this!
    POSTGRES_DB: str = "shopify_whatsapp"
    DATABASE_URL: str = "mysql+pymysql://root:@localhost/shopify_whatsapp"

    # Shopify
    SHOPIFY_WEBHOOK_SECRET: str = "your_webhook_secret"
    
    # WhatsApp
    WHATSAPP_API_TOKEN: str = "your_whatsapp_token"
    WHATSAPP_PHONE_NUMBER_ID: str = "your_phone_number_id"
    WHATSAPP_PROVIDER: str = "selenium" # Options: "official", "selenium"
    
    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

    def __init__(self, **data):
        super().__init__(**data)
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

settings = Settings()
