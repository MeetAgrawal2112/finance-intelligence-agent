# app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.core.config import settings

# bcrypt algorithm use karega password hash karne ke liye
# bcrypt isliye kyunki yeh intentionally slow hai
# Matlab brute force attack karna bahut mushkil ho jaata hai
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Plain text password ko hash mein convert karo.
    Example: "mypassword123" → "$2b$12$xyz..."
    Yeh one-way process hai — hash se password
    wapas nahi nikaal sakte.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Login ke time — user ne jo password diya
    usse stored hash se compare karo.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    JWT token banao.
    data mein user_id hoga: {"sub": "user-uuid-here"}
    Token expire hoga settings mein set time ke baad.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    # JWT encode karo secret key se
    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return token

def decode_access_token(token: str) -> dict | None:
    """
    Token verify karo aur data nikalo.
    Agar token invalid ya expired hai toh None return karo.
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