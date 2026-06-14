# app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    # Primary key — UUID use kar rahe hain integer ki jagah
    # Kyun? UUID globally unique hota hai, integer predictable hota hai
    # (koi /users/1, /users/2 guess kar sakta hai)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)

    # Password plain text kabhi store mat karo!
    # Hum bcrypt hash store karenge (Day 4 mein)
    hashed_password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Email verification

    # Currency preference — Indian users ke liye INR default
    currency = Column(String(10), default="INR")

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships — SQLAlchemy in sab ko automatically join karega
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user")
    budgets = relationship("Budget", back_populates="user")
    alerts = relationship("Alert", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"