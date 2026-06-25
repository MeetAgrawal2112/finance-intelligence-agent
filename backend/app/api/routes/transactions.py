# app/api/routes/transactions.py
from fastapi import (
    APIRouter, Depends, Query,
    UploadFile, File, HTTPException, status
)
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate,
    TransactionResponse, TransactionFilters,
    CSVImportResponse, MonthlySummary, CategoryAnalytics
)
from app.schemas.common import SuccessResponse
from app.services.transaction_service import TransactionService
from app.models.transaction import TransactionType

router = APIRouter()

@router.post(
    "",
    response_model=SuccessResponse[TransactionResponse],
    status_code=status.HTTP_201_CREATED
)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Naya transaction manually add karo."""
    transaction = TransactionService.create_transaction(db, current_user, data)
    return SuccessResponse(
        message="Transaction added successfully",
        data=TransactionResponse.model_validate(transaction)
    )

@router.get("", response_model=SuccessResponse)
def list_transactions(
    # Date filters
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    # Amount filters
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    # Type filter
    transaction_type: Optional[TransactionType] = Query(None),
    # Category filter
    category_id: Optional[UUID] = Query(None),
    # Search
    search: Optional[str] = Query(None, min_length=1),
    # Anomaly filter
    anomalies_only: bool = Query(False),
    # Pagination
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    # Sorting
    sort_by: str = Query("transaction_date"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Transactions list karo — filters, pagination, sorting ke saath.

    Examples:
    GET /transactions?search=swiggy
    GET /transactions?transaction_type=debit&start_date=2025-01-01
    GET /transactions?anomalies_only=true
    GET /transactions?page=2&page_size=10
    """
    filters = TransactionFilters(
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        transaction_type=transaction_type,
        category_id=category_id,
        search=search,
        anomalies_only=anomalies_only,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )

    transactions, total = TransactionService.get_transactions(
        db, current_user, filters
    )

    total_pages = -(-total // page_size)  # Ceiling division

    return SuccessResponse(
        data={
            "items": [
                TransactionResponse.model_validate(t)
                for t in transactions
            ],
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    )

@router.get("/summary", response_model=SuccessResponse[MonthlySummary])
def get_monthly_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Monthly summary — income, expenses, savings.
    Example: GET /transactions/summary?month=1&year=2025
    """
    summary = TransactionService.get_monthly_summary(
        db, current_user, month, year
    )
    return SuccessResponse(data=summary)

@router.get("/analytics", response_model=SuccessResponse)
def get_analytics(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Category-wise analytics — pie chart data.
    Example: GET /transactions/analytics?month=1&year=2025
    """
    analytics = TransactionService.get_category_analytics(
        db, current_user, month, year
    )
    return SuccessResponse(
        data={
            "categories": analytics,
            "total_categories": len(analytics)
        }
    )

@router.post("/import", response_model=SuccessResponse[CSVImportResponse])
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    CSV file se transactions bulk import karo.

    CSV format:
    date,amount,type,description,merchant
    2025-01-15,500,debit,Zomato Order,Zomato
    """
    # File type validate karo
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are accepted"
        )

    # File size limit — 5MB
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum 5MB allowed."
        )

    csv_content = content.decode('utf-8')
    result = TransactionService.import_from_csv(db, current_user, csv_content)

    return SuccessResponse(
        message=f"Import complete: {result['imported']} transactions added",
        data=CSVImportResponse(**result)
    )

@router.get("/{transaction_id}", response_model=SuccessResponse[TransactionResponse])
def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Single transaction detail dekho."""
    transaction = TransactionService.get_transaction_by_id(
        db, current_user, str(transaction_id)
    )
    return SuccessResponse(
        data=TransactionResponse.model_validate(transaction)
    )

@router.put("/{transaction_id}", response_model=SuccessResponse[TransactionResponse])
def update_transaction(
    transaction_id: UUID,
    update_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Transaction update karo — category, notes, merchant."""
    transaction = TransactionService.update_transaction(
        db, current_user, str(transaction_id), update_data
    )
    return SuccessResponse(
        message="Transaction updated successfully",
        data=TransactionResponse.model_validate(transaction)
    )

@router.delete("/{transaction_id}", response_model=SuccessResponse)
def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Transaction delete karo."""
    TransactionService.delete_transaction(
        db, current_user, str(transaction_id)
    )
    return SuccessResponse(message="Transaction deleted successfully")