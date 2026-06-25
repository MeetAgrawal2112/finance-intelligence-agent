# app/api/routes/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.common import SuccessResponse
from app.services.user_service import UserService
from app.core.security import create_access_token
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=SuccessResponse[UserResponse])
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Naya user register karo.
    Request body mein email, full_name, password chahiye.
    """
    user = UserService.create_user(db, user_data)
    return SuccessResponse(
        message="Registration successful! Please login.",
        data=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=SuccessResponse[TokenResponse])
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login karo aur JWT token lo.
    Is token ko baaki sab API calls mein
    Authorization: Bearer <token> header mein bhejo.
    """
    user = UserService.authenticate_user(
        db, credentials.email, credentials.password
    )

    # Token banao user ID ke saath
    token = create_access_token(data={"sub": str(user.id)})

    return SuccessResponse(
        message="Login successful!",
        data=TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
    )

@router.get("/me", response_model=SuccessResponse[UserResponse])
def get_me(current_user: User = Depends(get_current_user)):
    """
    Apna profile dekho.
    Protected endpoint — valid JWT token chahiye.
    """
    return SuccessResponse(
        data=UserResponse.model_validate(current_user)
    )