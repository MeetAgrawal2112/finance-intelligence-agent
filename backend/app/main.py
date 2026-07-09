# app/main.py — lifespan event add karo
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.routes import health, auth, transactions
from app.services.categoriser_service import categoriser



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    App startup aur shutdown events.
    Startup: ML models load karo
    Shutdown: Resources cleanup
    """
    # ── STARTUP ──
    print("\n🚀 Starting Finance Intelligence Agent...")
    print(f"   Environment: {settings.ENVIRONMENT}")

    # ML model load karo
    print("\n📦 Loading ML models...")
    categoriser.load_model()

    print("\n✅ App ready!\n")
    yield

    # ── SHUTDOWN ──
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

    # main.py mein add karo — transactions router ke baad
from app.api.routes import health, auth, transactions, ml   # ← ml add

app.include_router(
    ml.router,
    prefix="/api/v1/ml",
    tags=["ML Services"]
)