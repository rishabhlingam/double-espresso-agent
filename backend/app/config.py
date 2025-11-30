from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """
    Global application configuration.
    Note:
    - google_api_key is optional because in demo mode, users will provide 
      their own API key via frontend.
    """

    # GOOGLE ADK (optional for demo mode)
    google_api_key: Optional[str] = Field(
        None, 
        env="GOOGLE_API_KEY"
    )

    google_genai_use_vertexai: bool = Field(
        False, 
        env="GOOGLE_GENAI_USE_VERTEXAI"
    )

    # APP DATABASE (chat.db via SQLAlchemy)
    database_url: str = Field(..., env="DATABASE_URL")

    # ADK SESSION DATABASE (adk_sessions.db via DatabaseSessionService)
    adk_session_db_url: str = Field(
        "sqlite:///./adk_sessions.db",
        env="ADK_SESSION_DB_URL"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"


# Instantiate global settings
settings = Settings()
