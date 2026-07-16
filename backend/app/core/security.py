from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.core.config import settings
from enum import Enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

def hash_password(password: str) -> str:
    """Plain text → bcrypt hash."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Login ke time password verify karo."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Short-lived access token banao — 30 minutes.
    Har protected API call mein yeh bheja jaata hai.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({
        "exp": expire,
        "type": TokenType.ACCESS
    })
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def create_refresh_token(data: dict) -> str:
    """
    Long-lived refresh token banao — 7 days.
    Sirf naya access token lene ke liye use hota hai.
    Isko securely store karo — localStorage nahi, httpOnly cookie better hai.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({
        "exp": expire,
        "type": TokenType.REFRESH
    })
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def decode_token(token: str) -> dict | None:
    """
    Token decode karo aur payload return karo.
    Agar invalid/expired hai toh None return karo.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

def verify_token_type(payload: dict, expected_type: TokenType) -> bool:
    """
    Token ka type check karo.
    Refresh token se direct API access block karo.
    """
    return payload.get("type") == expected_type