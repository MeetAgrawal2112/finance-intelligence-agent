# app/api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse,
    TokenResponse, RefreshTokenRequest,
    UserUpdate, PasswordChange
)
from app.schemas.common import SuccessResponse
from app.services.user_service import UserService
from app.core.security import (
    create_access_token, create_refresh_token,
    decode_token, verify_token_type, TokenType
)
from app.core.config import settings
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

def _create_token_response(user: User) -> TokenResponse:
    """
    Helper function — user ke liye access + refresh token banao.
    Login aur token refresh dono mein yahi use hoga.
    """
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )

@router.post("/register", response_model=SuccessResponse[UserResponse],
             status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Naya account banao.
    Success pe 201 Created return hota hai (200 nahi).
    """
    user = UserService.create_user(db, user_data)
    return SuccessResponse(
        message="Account created successfully! Please login.",
        data=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=SuccessResponse[TokenResponse])
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login karo — access token aur refresh token dono milenge.
    Access token: 30 minutes valid
    Refresh token: 7 days valid
    """
    user = UserService.authenticate_user(
        db, credentials.email, credentials.password
    )
    token_data = _create_token_response(user)

    return SuccessResponse(
        message=f"Welcome back, {user.full_name}!",
        data=token_data
    )

@router.post("/refresh", response_model=SuccessResponse[TokenResponse])
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh token se naya access token lo.
    Frontend automatically yeh call karta hai jab
    access token expire ho jaata hai.
    """
    payload = decode_token(request.refresh_token)

    if not payload or not verify_token_type(payload, TokenType.REFRESH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token. Please login again."
        )

    user_id = payload.get("sub")
    user = UserService.get_user_by_id(db, user_id)
    token_data = _create_token_response(user)

    return SuccessResponse(
        message="Token refreshed successfully",
        data=token_data
    )

@router.get("/me", response_model=SuccessResponse[UserResponse])
def get_me(current_user: User = Depends(get_current_user)):
    """Apna profile dekho — protected route."""
    return SuccessResponse(
        data=UserResponse.model_validate(current_user)
    )

@router.put("/me", response_model=SuccessResponse[UserResponse])
def update_profile(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Profile update karo."""
    updated_user = UserService.update_profile(db, current_user, update_data)
    return SuccessResponse(
        message="Profile updated successfully",
        data=UserResponse.model_validate(updated_user)
    )

@router.post("/change-password", response_model=SuccessResponse)
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Password change karo."""
    UserService.change_password(db, current_user, password_data)
    return SuccessResponse(message="Password changed successfully!")

@router.post("/logout", response_model=SuccessResponse)
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout — client side se token delete karo.
    Server side pe JWT stateless hota hai isliye
    token blacklisting ke liye Redis use karna hoga (future mein).
    """
    return SuccessResponse(
        message=f"Goodbye, {current_user.full_name}! Logged out successfully."
    )