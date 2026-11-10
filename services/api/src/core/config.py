import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TN Government Grievance Portal"
    ENV: str = "development"
    SECRET_KEY: str = "tn-grievance-portal-super-secret-dev-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/tngrievance"
    )

    # Redis & Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

    # MinIO / Storage
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "grievance-attachments")

    # AI Adapters Configuration
    AI_STT_PROVIDER: str = os.getenv("AI_STT_PROVIDER", "mock")
    AI_TTS_PROVIDER: str = os.getenv("AI_TTS_PROVIDER", "mock")
    AI_ROUTING_PROVIDER: str = os.getenv("AI_ROUTING_PROVIDER", "mock")
    AI_DUPLICATE_PROVIDER: str = os.getenv("AI_DUPLICATE_PROVIDER", "mock")

    # Production AI API Keys (Optional)
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")

    class Config:
        case_sensitive = True

settings = Settings()
