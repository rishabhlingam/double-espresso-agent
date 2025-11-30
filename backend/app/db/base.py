from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

# Database Engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    echo=False,
    future=True,
)

# SessionLocal will be used for dependency injection
SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine,
)

# Base class for models
class Base(DeclarativeBase):
    pass
