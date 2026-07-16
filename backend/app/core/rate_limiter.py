# app/core/rate_limiter.py
"""
Rate Limiting — brute force attacks se bachao.
slowapi library use karta hai jo FastAPI ke saath kaam karta hai.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

def get_client_ip(request: Request) -> str:
    """
    Client IP nikalo.
    Proxy ke peeche hai toh X-Forwarded-For header se lo.
    """

    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return get_remote_address(request)

# Global limiter instance
limiter = Limiter(
    key_func=get_client_ip,
    default_limits=["200/minute"],  # Default — sab endpoints ke liye
)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom error response jab rate limit exceed ho."""
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "message": "Bahut zyada requests! Thodi der baad try karo.",
            "detail": f"Rate limit exceeded: {exc.detail}",
            "retry_after": "60 seconds",
        },
        headers={"Retry-After": "60"},
    )