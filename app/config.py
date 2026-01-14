"""
Configuration Management Module

This module handles all application settings and environment variables.
Using a centralized config makes it easy to:
1. Change settings without modifying code
2. Keep sensitive data (API keys) secure
3. Have different configs for dev/prod environments
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This must be called before accessing any env variables
load_dotenv()


class Settings:
    """
    Application settings loaded from environment variables.

    Why use a class?
    - Groups related settings together
    - Provides default values
    - Easy to validate settings
    - Can be imported anywhere in the app
    """

    # Groq Configuration (FREE and FAST!)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    # Document Settings
    MAX_FILE_SIZE_MB: int = 10  # Maximum upload size in MB
    ALLOWED_EXTENSIONS: list = [".pdf"]

    # Application Settings
    APP_NAME: str = "AI Document Q&A Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"


# Create a single instance to be imported throughout the app
settings = Settings()
