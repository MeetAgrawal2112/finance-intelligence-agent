# app/core/security_middleware.py
"""
Security middleware — har request pe security headers add karo.
OWASP recommendations follow karta hai.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers automatically add karo sab responses mein.
    Yeh headers browsers ko instruct karte hain
    security policies follow karne ke liye.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        # Request timing
        process_time = time.time() - start_time

        # ── Security Headers ──────────────────────────────────────
        # Clickjacking se bachao
        response.headers["X-Frame-Options"] = "DENY"

        # MIME type sniffing se bachao
        response.headers["X-Content-Type-Options"] = "nosniff"

        # XSS protection (older browsers ke liye)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # HTTPS enforce karo (production mein)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        # Content Security Policy — kahan se content load ho sakta hai
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.groq.com;"
        )

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=()"
        )

        # Server info chhupao
        response.headers["X-Powered-By"] = ""

        # Request timing header (debugging ke liye)
        response.headers["X-Process-Time"] = str(process_time)

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Security-relevant requests log karo.
    Suspicious activity detect karne ke liye.
    """

    SENSITIVE_PATHS = [
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
    ]

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Auth endpoints ke liye detailed logging
        if request.url.path in self.SENSITIVE_PATHS:
            client_ip = request.headers.get(
                "X-Forwarded-For",
                request.client.host if request.client else "unknown"
            )

            log_level = logging.WARNING if response.status_code >= 400 else logging.INFO

            logger.log(
                log_level,
                f"AUTH | {request.method} {request.url.path} | "
                f"Status: {response.status_code} | "
                f"IP: {client_ip} | "
                f"UA: {request.headers.get('user-agent', 'unknown')[:50]}"
            )

        return response