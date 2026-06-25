# app/api/routes/transactions.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.schemas.common import SuccessResponse, PaginatedResponse
import uuid
from datetime import datetime, timezone

router = APIRouter()

@router.post("", response_model=SuccessResponse[TransactionResponse])
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Naya transaction add karo."""
    transaction = Transaction(
        id=uuid.uuid4(),
        user_id=current_user.id,
        **transaction_data.model_dump()
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return SuccessResponse(
        message="Transaction added successfully",
        data=TransactionResponse.model_validate(transaction)
    )

@router.get("", response_model=SuccessResponse)
def get_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apni saari transactions dekho."""
    offset = (page - 1) * page_size
    total = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).count()

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).offset(offset).limit(page_size).all()

    return SuccessResponse(
        data={
            "items": [TransactionResponse.model_validate(t) for t in transactions],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": -(-total // page_size)  # Ceiling division
        }
    )