from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings
import redis as redis_client
from datetime import datetime, timezone

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    from app.services.cache_service import cache

    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": {}
    }

    # PostgreSQL check
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "✅ connected"
    except Exception as e:
        health_status["services"]["database"] = f"❌ {str(e)[:50]}"
        health_status["status"] = "unhealthy"

    # Redis check
    health_status["services"]["redis"] = (
        "✅ connected" if cache.is_connected else "⚠️ not available"
    )

    # ML Models
    from app.services.categoriser_service import categoriser
    from app.services.anomaly_service import anomaly_detector
    from app.services.prediction_service import predictor

    health_status["ml_models"] = {
        "categoriser": "✅ loaded" if categoriser.is_loaded else "❌ not loaded",
        "anomaly_detector": "✅ loaded" if anomaly_detector.is_loaded else "❌ not loaded",
        "predictor": "✅ loaded" if predictor.is_loaded else "❌ not loaded",
    }

    return health_status