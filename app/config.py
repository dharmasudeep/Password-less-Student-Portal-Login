"""Configuration objects for the Flask application."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import os

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_PATH = BASE_DIR / "instance"
INSTANCE_PATH.mkdir(exist_ok=True)


def _get_env(name: str, default: Any) -> Any:
    return os.getenv(name, default)


class Config:
    SECRET_KEY = _get_env("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = _get_env(
        "DATABASE_URL", f"sqlite:///{INSTANCE_PATH / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_HTTPONLY = True
    WTF_CSRF_TIME_LIMIT = None
    RATE_LIMIT = _get_env("RATE_LIMIT", "30/minute")
    OLLAMA_HOST = _get_env("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = _get_env("OLLAMA_MODEL", "llama3")
    SITE_NAME = "Password-less"
    PREFERRED_URL_SCHEME = "https" if _get_env("FLASK_ENV", "development") == "production" else "http"


class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite+pysqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    RATE_LIMIT = "1000/minute"
