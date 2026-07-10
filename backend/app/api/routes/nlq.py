# app/api/routes/nlq.py
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import json

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.common import SuccessResponse

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    chat_history: Optional[List[dict]] = []

class QueryResponse(BaseModel):
    answer: str
    success: bool
    query: str
    error: Optional[str] = None

@router.post("/query", response_model=SuccessResponse[QueryResponse])
def process_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Natural language query process karo.

    Examples:
    - "Is mahine maine sabse zyada kahan kharch kiya?"
    - "Kitna save kar sakta hoon?"
    - "Meri last 5 transactions dikhao"
    - "Koi suspicious transaction hai?"
    - "Next month ka forecast kya hai?"
    """
    from app.services.langchain.agent import run_finance_query

    result = run_finance_query(
        query=request.query,
        db=db,
        user_id=str(current_user.id),
        chat_history=request.chat_history
    )

    return SuccessResponse(
        message="Query processed",
        data=QueryResponse(**result)
    )

@router.get("/suggestions")
def get_query_suggestions(
    current_user: User = Depends(get_current_user)
):
    """
    Suggested queries — frontend chat mein chips ke roop mein dikhao.
    """
    suggestions = [
        {
            "text": "Is mahine maine kahan kharch kiya?",
            "category": "spending"
        },
        {
            "text": "Kitna save kar sakta hoon?",
            "category": "savings"
        },
        {
            "text": "Meri last 10 transactions dikhao",
            "category": "history"
        },
        {
            "text": "Koi suspicious transaction hai?",
            "category": "security"
        },
        {
            "text": "Next month ka spending forecast kya hai?",
            "category": "forecast"
        },
        {
            "text": "Dining pe kitna kharch hua is mahine?",
            "category": "category"
        },
        {
            "text": "Groceries ka budget kaisa chal raha hai?",
            "category": "budget"
        },
        {
            "text": "Mera savings rate kya hai?",
            "category": "savings"
        },
    ]

    return SuccessResponse(data={"suggestions": suggestions})