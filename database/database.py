import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

server = os.getenv("DB_SERVER", "localhost")
port = os.getenv("DB_PORT", "5433")
DATABASE_URL = f"postgresql://llm:llm@{server}:{port}/chatmed_pipeline"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
