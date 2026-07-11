# app/main.py — lifespan event add karo
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.routes import health, auth, transactions
from app.services.categoriser_service import categoriser
from app.services.anomaly_service import anomaly_detector
from app.services.prediction_service import predictor  # ← ADD
from app.api.routes import health, auth, transactions, ml, nlq
# app/main.py mein lifespan update karo
from app.services.cache_service import cache
from app.api.routes import health, auth, transactions, ml, nlq, alerts

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🚀 Starting Finance Intelligence Agent...")

    # Redis connect
    print("\n🔴 Connecting to Redis...")
    cache.connect()

    # ML models load
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
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan   # ← ADD
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)
app.include_router(
    transactions.router,
    prefix="/api/v1/transactions",
    tags=["Transactions"]
)

@app.get("/", tags=["Root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "ml_models": {
            "categoriser": categoriser.model_info
        }
    }

app.include_router(
    nlq.router,
    prefix="/api/v1/nlq",
    tags=["Natural Language Queries"]
)

app.include_router(
    alerts.router,
    prefix="/api/v1/alerts",
    tags=["Alerts"]
)