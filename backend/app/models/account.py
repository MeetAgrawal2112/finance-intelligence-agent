# app/models/account.py
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum
from app.db.base import Base

class AccountType(str, enum.Enum):
    """Account ke types"""
    SAVINGS = "savings"
    CURRENT = "current"
    CREDIT_CARD = "credit_card"
    WALLET = "wallet"          # Paytm, PhonePe, etc.
    INVESTMENT = "investment"  # Mutual funds, stocks

class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    account_name = Column(String(255), nullable=False)   # "HDFC Savings", "SBI Credit Card"
    account_type = Column(Enum(AccountType), default=AccountType.SAVINGS)
    bank_name = Column(String(255))                      # "HDFC Bank", "SBI"
    account_number_last4 = Column(String(4))             # Security ke liye sirf last 4 digits
    balance = Column(Float, default=0.0)                 # Current balance
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")

    def __repr__(self):
        return f"<Account {self.account_name} - {self.bank_name}>"