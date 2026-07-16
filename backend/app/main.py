from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from app.core.security_middleware import (
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware
)
from app.api.routes import health, auth, transactions, ml, nlq, alerts
from app.services.categoriser_service import categoriser
from app.services.anomaly_service import anomaly_detector
from app.services.prediction_service import predictor
from app.services.cache_service import cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🚀 Starting Finance Intelligence Agent...")
    print(f"   Environment: {settings.ENVIRONMENT}")

    print("\n🔴 Connecting to Redis...")
    cache.connect()

    print("\n📦 Loading ML models...")
    categoriser.load_model()
    anomaly_detector.load_model()
    predictor.load_model()

    print("\n✅ App ready!\n")
    yield
    print("\n👋 Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered personal finance agent",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# ── Rate Limiter ───────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# ── Security Middleware ────────────────────────────────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    max_age=3600,
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(
    transactions.router,
    prefix="/api/v1/transactions",
    tags=["Transactions"]
)
app.include_router(ml.router, prefix="/api/v1/ml", tags=["ML"])
app.include_router(nlq.router, prefix="/api/v1/nlq", tags=["NLQ"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])

@app.get("/", tags=["Root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }