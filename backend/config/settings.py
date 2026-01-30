from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Mistral AI
    mistral_api_key: str

    # LangSmith Observability
    langsmith_api_key: str | None = None
    langsmith_project: str = "hr-ai-assistant"
    langsmith_tracing: bool = True

    # Database
    database_url: str = "sqlite:///./hr_database.db"

    # Vector Store
    vector_store_path: str = "./vector_store"
    hr_policies_path: str = "./data/hr_policies"

    # External HR System APIs (mock endpoints for demo)
    hr_api_base_url: str = "http://localhost:8000/api/v1/hr-system"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def setup_langsmith():
    """Configure LangSmith for observability"""
    settings = get_settings()
    if settings.langsmith_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        print(f"✓ LangSmith tracing enabled for project: {settings.langsmith_project}")
