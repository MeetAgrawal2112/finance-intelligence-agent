from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_token, verify_token_type, TokenType
from app.models.user import User
from uuid import UUID as PyUUID

bearer_scheme = HTTPBearer(
    scheme_name="JWT Bearer Token",
    description="Paste your access token here. Get it from /api/v1/auth/login"
)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Protected routes ke liye — valid access token chahiye.

    Kaise kaam karta hai:
    1. Header se token nikalo: Authorization: Bearer <token>
    2. Token decode karo
    3. Token type check karo (access hona chahiye, refresh nahi)
    4. User ID se user dhundho DB mein
    5. User active hai? Check karo
    6. User object return karo
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token. Please login again.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise credentials_exception

    # Refresh token se API access block karo
    if not verify_token_type(payload, TokenType.ACCESS):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Use access token, not refresh token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    try:
        user_uuid = PyUUID(user_id)
    except ValueError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_uuid).first()

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled"
        )

    return user

def get_current_user_optional(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(
        HTTPBearer(auto_error=False)
    )
) -> User | None:
    """
    Optional auth — token ho toh user return karo, na ho toh None.
    Public endpoints ke liye jo logged-in users ko extra data dete hain.
    """
    if not credentials:
        return None
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None