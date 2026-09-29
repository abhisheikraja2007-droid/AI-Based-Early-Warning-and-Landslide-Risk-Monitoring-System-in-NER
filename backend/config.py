"""
Backend Configuration and Environment Settings.
"""

import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    BaseSettings = object


class Settings:
    PROJECT_NAME: str = "Landslide Early Warning & Hazard Assessment System"
    VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Model filepaths
    PYTORCH_SPATIAL_MODEL_PATH: str = os.getenv("PYTORCH_SPATIAL_MODEL_PATH", "checkpoints/landslide_spatial_unet_best.pt")
    XGBOOST_TEMPORAL_MODEL_PATH: str = os.getenv("XGBOOST_TEMPORAL_MODEL_PATH", "checkpoints/landslide_temporal_xgboost.json")
    NC_RAINFALL_PATH: str = os.getenv("NC_RAINFALL_PATH", "RF25_ind2025_rfp25.nc")

    # Task Queue Broker (Redis)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # MongoDB Cluster Configuration
    MONGODB_URL: str = os.getenv(
        "MONGODB_URL",
        "mongodb://localhost:27017"
    )
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "landslide_sih_db")
    CITIZEN_REPORTS_COLLECTION: str = "citizen_reports"

    # Storage paths
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads/citizen_photos")


settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
