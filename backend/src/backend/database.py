import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Update this URL with your actual PostgreSQL credentials
# Format: postgresql://username:password@localhost:5432/database_name
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:post%402026@localhost:5432/chatbot_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get DB session in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
