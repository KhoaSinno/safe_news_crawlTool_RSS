"""
Centralized Configuration and Settings for Safe News Crawler Backend.
All environment variables and application settings must be accessed through this module.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# Load .env file once upon import
load_dotenv(override=True)


@dataclass
class Settings:
    """Application settings mapped from environment variables with strong typing and fallbacks."""

    # Gemini AI Configuration
    GEMINI_API_KEY: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip()
    )
    GEMINI_MODEL: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    )

    # Firebase Configuration
    FIREBASE_SERVICE_ACCOUNT: Optional[str] = field(
        default_factory=lambda: os.getenv("FIREBASE_SERVICE_ACCOUNT")
    )
    FIREBASE_CREDENTIALS_PATH: str = field(
        default_factory=lambda: os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json").strip()
    )
    FIREBASE_PROJECT_ID: Optional[str] = field(
        default_factory=lambda: os.getenv("FIREBASE_PROJECT_ID")
    )
    FIREBASE_DATABASE_URL: Optional[str] = field(
        default_factory=lambda: os.getenv("FIREBASE_DATABASE_URL")
    )

    # Firestore Collections
    PROD_COLLECTION: str = field(
        default_factory=lambda: os.getenv("PROD_COLLECTION", "positive_news").strip()
    )
    TEST_COLLECTION: str = field(
        default_factory=lambda: os.getenv("TEST_COLLECTION", "positive_news_test").strip()
    )
    REPORTS_COLLECTION: str = field(
        default_factory=lambda: os.getenv("REPORTS_COLLECTION", "news_reports").strip()
    )

    # Crawler Settings & State
    CRAWL_STATE_FILE: str = field(
        default_factory=lambda: os.getenv("CRAWL_STATE_FILE", "crawl_state.json").strip()
    )
    MAX_PROCESSED_LINKS: int = field(
        default_factory=lambda: int(os.getenv("MAX_PROCESSED_LINKS", "2000"))
    )
    MAX_CHARS_PER_ARTICLE: int = field(
        default_factory=lambda: int(os.getenv("MAX_CHARS_PER_ARTICLE", "2000"))
    )
    RATE_LIMIT_SECONDS: float = field(
        default_factory=lambda: float(os.getenv("RATE_LIMIT_SECONDS", "2.0"))
    )

    # Logging Configuration
    LOG_FILE: str = field(
        default_factory=lambda: os.getenv("LOG_FILE", "news_crawler.log").strip()
    )
    LOG_LEVEL: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").strip()
    )

    def validate(self) -> None:
        """Validate critical configuration settings."""
        if not self.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is missing! Please set GEMINI_API_KEY in your .env file."
            )

    def reload(self) -> None:
        """Re-read .env and update configuration settings dynamically."""
        load_dotenv(override=True)
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.FIREBASE_SERVICE_ACCOUNT = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        self.FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json").strip()
        self.FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
        self.FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
        self.PROD_COLLECTION = os.getenv("PROD_COLLECTION", "positive_news").strip()
        self.TEST_COLLECTION = os.getenv("TEST_COLLECTION", "positive_news_test").strip()
        self.REPORTS_COLLECTION = os.getenv("REPORTS_COLLECTION", "news_reports").strip()
        self.CRAWL_STATE_FILE = os.getenv("CRAWL_STATE_FILE", "crawl_state.json").strip()
        self.MAX_PROCESSED_LINKS = int(os.getenv("MAX_PROCESSED_LINKS", "2000"))
        self.MAX_CHARS_PER_ARTICLE = int(os.getenv("MAX_CHARS_PER_ARTICLE", "2000"))
        self.RATE_LIMIT_SECONDS = float(os.getenv("RATE_LIMIT_SECONDS", "2.0"))
        self.LOG_FILE = os.getenv("LOG_FILE", "news_crawler.log").strip()
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip()


# Singleton global instance
settings = Settings()
