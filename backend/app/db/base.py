# app/db/base.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime
from datetime import datetime, timezone

class Base(DeclarativeBase):
    """
    Yeh sab models ka parent class hai.
    Har table automatically created_at aur updated_at
    columns inherit karega is class se.
    """
    pass