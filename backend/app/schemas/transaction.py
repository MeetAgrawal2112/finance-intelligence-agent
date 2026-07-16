from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.transaction import TransactionType, TransactionStatus

class TransactionCreate(BaseModel):
    """Naya transaction add karne ke liye."""
    amount: float = Field(..., gt=0)
    currency: str = Field(default="INR", max_length=10)
    transaction_type: TransactionType
    description: str = Field(..., min_length=1, max_length=500)
    merchant_name: Optional[str] = Field(None, max_length=255)
    transaction_date: datetime
    account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    notes: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def round_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return round(v, 2)

class TransactionUpdate(BaseModel):
    """Transaction update — sab optional."""
    category_id: Optional[UUID] = None
    notes: Optional[str] = None
    merchant_name: Optional[str] = None
    description: Optional[str] = None
    is_manually_categorized: Optional[bool] = None

class TransactionResponse(BaseModel):
    """API response mein transaction data."""
    id: UUID
    amount: float
    currency: str
    transaction_type: TransactionType
    status: TransactionStatus
    description: str
    merchant_name: Optional[str]
    transaction_date: datetime
    category_id: Optional[UUID]
    account_id: Optional[UUID]
    is_anomaly: bool
    anomaly_score: float
    ml_category_confidence: float
    is_manually_categorized: bool
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

class TransactionFilters(BaseModel):
    """
    GET /transactions ke filters.
    Sab optional hain — jo chahiye woh do.
    """
    # Date range
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Amount range
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None

    # Type filter
    transaction_type: Optional[TransactionType] = None

    # Category filter
    category_id: Optional[UUID] = None

    # Search
    search: Optional[str] = None  # merchant_name ya description mein search

    # Anomaly filter
    anomalies_only: bool = False

    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    # Sorting
    sort_by: str = Field(default="transaction_date")
    sort_order: str = Field(default="desc")

class CSVImportResponse(BaseModel):
    """CSV import ka result."""
    total_rows: int
    imported: int
    skipped: int
    errors: List[str]

class MonthlySummary(BaseModel):
    """Monthly spending summary."""
    month: int
    year: int
    total_income: float
    total_expenses: float
    net_savings: float
    transaction_count: int
    top_category: Optional[str]

class CategoryAnalytics(BaseModel):
    """Category-wise analytics."""
    category_id: Optional[UUID]
    category_name: str
    total_amount: float
    transaction_count: int
    percentage: float
    avg_transaction: float