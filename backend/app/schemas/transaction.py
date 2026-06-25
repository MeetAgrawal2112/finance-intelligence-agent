# app/schemas/transaction.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.transaction import TransactionType, TransactionStatus

class TransactionCreate(BaseModel):
    """Naya transaction add karne ke liye."""
    amount: float = Field(..., gt=0, description="Amount must be positive")
    currency: str = Field(default="INR", max_length=10)
    transaction_type: TransactionType
    description: str = Field(..., min_length=1, max_length=500)
    merchant_name: Optional[str] = None
    transaction_date: datetime
    account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    notes: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return round(v, 2)  # 2 decimal places tak round karo

class TransactionResponse(BaseModel):
    """Transaction response."""
    id: UUID
    amount: float
    currency: str
    transaction_type: TransactionType
    status: TransactionStatus
    description: str
    merchant_name: Optional[str]
    transaction_date: datetime
    is_anomaly: bool
    anomaly_score: float
    ml_category_confidence: float
    is_manually_categorized: bool
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

class TransactionUpdate(BaseModel):
    """Transaction update — mainly category manual override ke liye."""
    category_id: Optional[UUID] = None
    notes: Optional[str] = None
    is_manually_categorized: Optional[bool] = None