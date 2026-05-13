import os
from pydantic_settings import BaseSettings

# Hugging Face Spaces provides a persistent /data directory.
# All persistent data (DB, vectors, uploads) must live there
# to survive container restarts and rebuilds.
PERSISTENT_DIR = os.getenv("PERSISTENT_DIR", "/data")

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{PERSISTENT_DIR}/sql_app.db"
    )
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", f"{PERSISTENT_DIR}/chroma_db")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", f"{PERSISTENT_DIR}/uploads")
    LLM_PROVIDER: str = "ollama"
    GEMINI_API_KEY: str = ""
    OLLAMA_URL: str = "http://host.docker.internal:11434"
    OLLAMA_MODEL: str = "qwen2.5:1.5b"
    REDIS_URL: str = "redis://redis:6379"
    SECRET_KEY: str = "supersecretkey_please_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

settings = Settings()
