# app/api/routes/health.py
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
    """
    App ka health check — kya sab systems chal rahe hain?
    Production mein load balancer yeh endpoint check karta hai.
    Agar 200 aaye → app alive
    Agar 500 aaye → app dead → restart karo
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {}
    }

    # PostgreSQL check
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "✅ connected"
    except Exception as e:
        health_status["services"]["database"] = f"❌ error: {str(e)}"
        health_status["status"] = "unhealthy"

    # Redis check
    try:
        r = redis_client.from_url(settings.REDIS_URL)
        r.ping()
        health_status["services"]["redis"] = "✅ connected"
    except Exception as e:
        health_status["services"]["redis"] = f"❌ error: {str(e)}"

    return health_status