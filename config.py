import os
from decouple import config


class Config:
    SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-in-production")
    DEBUG = config("DEBUG", default=True, cast=bool)

    # Database
    SQLALCHEMY_DATABASE_URI = config("DATABASE_URL", default="sqlite:///links.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Core Auth System
    AUTH_SYSTEM_URL = config("AUTH_SYSTEM_URL", default="http://localhost:8000")
    AUTH_API_KEY = config("AUTH_API_KEY", default="change-this-secure-key")
