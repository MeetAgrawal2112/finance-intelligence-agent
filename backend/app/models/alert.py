# app/models/alert.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum
from app.db.base import Base

class AlertType(str, enum.Enum):
    ANOMALY = "anomaly"              # Unusual transaction detect hui
    BUDGET_WARNING = "budget_warning"  # 80% budget use ho gaya
    BUDGET_EXCEEDED = "budget_exceeded"  # Budget cross ho gaya
    LARGE_TRANSACTION = "large_transaction"  # Single bada transaction
    DUPLICATE = "duplicate"          # Same amount same merchant dobara

class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Agar alert kisi specific transaction ke baare mein hai
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True)

    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM)

    title = Column(String(255), nullable=False)  # "Unusual transaction detected"
    message = Column(Text, nullable=False)        # Detailed explanation

    is_read = Column(Boolean, default=False)      # User ne dekha ya nahi
    is_resolved = Column(Boolean, default=False)  # User ne action liya ya nahi

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="alerts")
    transaction = relationship("Transaction", back_populates="alerts")

    def __repr__(self):
        return f"<Alert {self.alert_type} - {self.severity}>"