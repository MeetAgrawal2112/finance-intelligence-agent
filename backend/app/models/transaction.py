from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum
from app.db.base import Base

class TransactionType(str, enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.COMPLETED)

    description = Column(String(500), nullable=False)

    merchant_name = Column(String(255))
    merchant_category = Column(String(100))

    transaction_date = Column(DateTime(timezone=True), nullable=False)

    ml_category_confidence = Column(Float, default=0.0)
    is_manually_categorized = Column(Boolean, default=False)

    # Anomaly detection
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)  # 0=normal, 1=highly suspicious

    # Vector embedding ke liye (pgvector Day 13 mein)
    # embedding = Column(Vector(1536))  # OpenAI ada-002 = 1536 dimensions

    # Notes
    notes = Column(Text)  # User ka personal note

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    alerts = relationship("Alert", back_populates="transaction")

    def __repr__(self):
        return f"<Transaction {self.merchant_name} ₹{self.amount} {self.transaction_type}>"