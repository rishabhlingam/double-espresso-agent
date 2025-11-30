from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """
    Global application configuration.
    Google_api_key is optional.
    Users will provide own API key via frontend.
    """

    # GOOGLE ADK (optional)
    google_api_key: Optional[str] = Field(
        None, 
        env="GOOGLE_API_KEY"
    )

    google_genai_use_vertexai: bool = Field(
        False, 
        env="GOOGLE_GENAI_USE_VERTEXAI"
    )

    # APP DATABASE
    database_url: str = Field(..., env="DATABASE_URL")

    # ADK SESSION DATABASE
    adk_session_db_url: str = Field(
        "sqlite:///./adk_sessions.db",
        env="ADK_SESSION_DB_URL"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
