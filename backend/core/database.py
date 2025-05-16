from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app_longevity_saas.backend.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={} if settings.DATABASE_URL.startswith("postgresql") else {"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
