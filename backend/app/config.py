from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # GOOGLE ADK
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    google_genai_use_vertexai: bool = Field(False, env="GOOGLE_GENAI_USE_VERTEXAI")

    # DATABASE
    database_url: str = Field(..., env="DATABASE_URL")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
