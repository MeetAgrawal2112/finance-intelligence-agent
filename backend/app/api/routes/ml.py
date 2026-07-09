# app/api/routes/ml.py
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.services.categoriser_service import categoriser
from app.schemas.common import SuccessResponse
from pydantic import BaseModel
from typing import List

router = APIRouter()

class CategoriseRequest(BaseModel):
    description: str
    merchant_name: str = ""

class BatchCategoriseRequest(BaseModel):
    descriptions: List[str]

@router.post("/categorise")
def categorise_transaction(
    request: CategoriseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Single transaction categorise karo.
    """
    text = f"{request.merchant_name} {request.description}".strip()
    result = categoriser.predict(text)

    return SuccessResponse(
        message="Category predicted",
        data=result
    )

@router.post("/categorise/batch")
def categorise_batch(
    request: BatchCategoriseRequest,
    current_user: User = Depends(get_current_user)
):
    """Multiple transactions ek saath categorise karo."""
    results = categoriser.predict_batch(request.descriptions)
    return SuccessResponse(
        message=f"{len(results)} transactions categorised",
        data={"predictions": results}
    )

@router.get("/model-info")
def get_model_info(current_user: User = Depends(get_current_user)):
    """ML model ka status aur info."""
    return SuccessResponse(
        data=categoriser.model_info
    )