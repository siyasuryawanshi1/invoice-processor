import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Google Cloud Configuration
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    PROCESSOR_ID = os.getenv("DOCUMENT_AI_PROCESSOR_ID")
    PROCESSOR_LOCATION = os.getenv("DOCUMENT_AI_LOCATION", "us")
    CREDENTIALS_PATH = "config/credentials.json"

    # File Configuration
    UPLOAD_DIR = Path("data/uploads")
    PROCESSED_DIR = Path("data/processed")
    EXPORT_DIR = Path("data/exports")

    # App Configuration
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]

    # Create directories
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()