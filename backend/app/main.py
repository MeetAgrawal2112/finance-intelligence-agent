# app/main.py  ← backend/ folder ke andar banao
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import health, auth, transactions

# FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered personal finance agent",
    # Swagger UI aur ReDoc URLs
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware — Frontend ko allow karo
# Bina iske browser block kar deta hai API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PUT, DELETE sab
    allow_headers=["*"],
)

# Routers register karo — prefix se URL ban jaata hai
# health router → /health
# auth router → /api/v1/auth/login, /api/v1/auth/register
# transactions router → /api/v1/transactions
app.include_router(
    health.router,
    tags=["Health"]
)
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
    """API root — basic info."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }