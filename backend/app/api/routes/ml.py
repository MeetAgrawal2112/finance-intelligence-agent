from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.services.categoriser_service import categoriser
from app.schemas.common import SuccessResponse
from pydantic import BaseModel
from typing import List
from app.services.anomaly_service import anomaly_detector
from datetime import datetime, timezone
from app.services.prediction_service import predictor
from app.db.session import get_db
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


class AnomalyCheckRequest(BaseModel):
    amount: float
    description: str
    transaction_date: str = None

@router.post("/anomaly-check")
def check_anomaly(
    request: AnomalyCheckRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Transaction anomaly check karo add karne se pehle.
    Frontend preview ke liye use kar sakta hai.
    """
    t_date = datetime.now(timezone.utc)
    if request.transaction_date:
        try:
            t_date = datetime.fromisoformat(request.transaction_date)
        except:
            pass

    result = anomaly_detector.analyze_transaction(
        amount=request.amount,
        description=request.description,
        transaction_date=t_date,
        user_id=str(current_user.id),
    )

    return SuccessResponse(
        message="Anomaly check complete",
        data=result
    )

@router.get("/anomaly-stats")
def get_anomaly_stats(
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """User ke anomaly statistics."""
    from app.models.transaction import Transaction
    from app.models.alert import Alert

    total = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.is_anomaly == True
    ).count()

    unread_alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.is_read == False
    ).count()

    return SuccessResponse(
        data={
            "total_anomalies": total,
            "unread_alerts": unread_alerts,
            "detector_loaded": anomaly_detector.is_loaded
        }
    )



@router.get("/forecast")
def get_spending_forecast(
    current_user: User = Depends(get_current_user)
):
    """
    Next 30 days ka spending forecast.
    Dashboard forecast page ke liye.
    """
    forecast = predictor.predict_next_month()
    return SuccessResponse(
        message="Forecast generated",
        data=forecast
    )

@router.get("/forecast/{category}")
def get_category_forecast(
    category: str,
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Single category ka detailed forecast."""
    result = predictor.predict_category(category, days)
    return SuccessResponse(data=result)

@router.get("/savings-advice")
def get_savings_advice(
    monthly_income: float = 50000,
    current_user: User = Depends(get_current_user)
):
    """
    Savings advice based on predicted expenses.
    50-30-20 rule use karta hai.
    """
    forecast = predictor.predict_next_month()
    total_predicted = forecast.get("total_predicted", 0)

    advice = predictor.get_savings_advice(total_predicted, monthly_income)

    return SuccessResponse(
        message=advice["message"],
        data={
            **advice,
            "forecast": forecast,
        }
    )