from sqlalchemy import Column, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.db.base import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)

    amount = Column(Float, nullable=False)
    spent_amount = Column(Float, default=0.0)

    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    alert_threshold = Column(Float, default=0.8)
    is_alert_sent = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True),
                        default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets"

    def __repr__(self):
        return f"<Budget ₹{self.amount} for {self.category_id} - {self.month}/{self.year}>"