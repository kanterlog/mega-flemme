"""
⚙️ Configuration KanterMator
Phase 2.1 - Configuration centralisée

Gestion de tous les paramètres de l'application
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Configuration centralisée de l'application KanterMator"""
    
    # 🚀 Application
    APP_NAME: str = "KanterMator"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    SECRET_KEY: str = Field(env="SECRET_KEY")
    
    # 🗄️ Base de données
    DATABASE_URL: str = Field(env="DATABASE_URL")
    
    # 🔴 Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # 🔑 Google Workspace
    GOOGLE_CLIENT_ID: str = Field(env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(env="GOOGLE_CLIENT_SECRET") 
    GOOGLE_SHEETS_ID: str = Field(env="GOOGLE_SHEETS_ID")
    GOOGLE_CREDENTIALS_PATH: str = Field(default="/app/credentials/google-credentials.json", env="GOOGLE_CREDENTIALS_PATH")
    
    # 📂 Google Drive IDs
    DRIVE_CAHIER_JOURNAL_ID: str = Field(env="DRIVE_CAHIER_JOURNAL_ID")
    DRIVE_ARCHIVE_ID: str = Field(env="DRIVE_ARCHIVE_ID")
    
    # 🤖 IA Hybride - GPT + Gemini pour Sylvie
    OPENAI_API_KEY: str = Field(env="OPENAI_API_KEY")
    GOOGLE_AI_KEY: str = Field(default="", env="GOOGLE_AI_KEY")
    AI_MODEL_STRATEGY: str = Field(default="hybrid", env="AI_MODEL_STRATEGY")  # hybrid|openai|gemini
    PRIMARY_MODEL: str = Field(default="openai", env="PRIMARY_MODEL")
    FALLBACK_MODEL: str = Field(default="gemini", env="FALLBACK_MODEL")
    OPENAI_MODEL: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    GEMINI_MODEL: str = Field(default="gemini-1.5-pro", env="GEMINI_MODEL")
    
    # 📧 Notifications
    EMAIL_HOST: str = Field(default="smtp.gmail.com", env="EMAIL_HOST")
    EMAIL_PORT: int = Field(default=587, env="EMAIL_PORT")
    EMAIL_USERNAME: str = Field(env="EMAIL_USERNAME")
    EMAIL_PASSWORD: str = Field(env="EMAIL_PASSWORD")
    
    # 🌐 Réseau
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "https://your-domain.com"],
        env="ALLOWED_ORIGINS"
    )
    
    # 📊 Monitoring
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # ⏰ Scheduler KanterMator
    AUTOMATION_ENABLED: bool = Field(default=True, env="AUTOMATION_ENABLED")
    AUTOMATION_SCHEDULE: str = Field(default="0 23 * * 6", env="AUTOMATION_SCHEDULE")  # Samedi 23h
    AUTOMATION_TIMEZONE: str = Field(default="Europe/Paris", env="AUTOMATION_TIMEZONE")
    
    # 🎯 Progressions pédagogiques
    SCHOOL_YEAR_START: str = Field(default="2025-09-01", env="SCHOOL_YEAR_START")
    SCHOOL_YEAR_END: str = Field(default="2026-07-31", env="SCHOOL_YEAR_END")
    SUBJECTS: List[str] = Field(
        default=[
            "Français", "Dictée", "Maths", "Calcul mental",
            "Histoire", "Sciences", "Géographie"
        ],
        env="SUBJECTS"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore les variables non définies

# Instance globale des settings
settings = Settings()
