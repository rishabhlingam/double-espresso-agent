from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # GOOGLE ADK
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    google_genai_use_vertexai: bool = Field(False, env="GOOGLE_GENAI_USE_VERTEXAI")

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

settings = Settings()
