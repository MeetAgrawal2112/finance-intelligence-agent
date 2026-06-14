# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/finance_db"
)

# Engine = actual database connection
# pool_pre_ping=True matlab har query se pehle
# connection alive hai ya nahi check karta hai
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True   # Development mein SQL queries print hogi
)

# SessionLocal = har request ke liye ek DB session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """
    FastAPI dependency injection ke liye.
    Har API request ko ek fresh DB session milega,
    aur request khatam hone pe automatically close hoga.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()