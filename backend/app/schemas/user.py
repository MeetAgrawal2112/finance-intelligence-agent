# app/schemas/user.py — poora file replace karo
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=100)
    currency: str = Field(default="INR", max_length=10)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    currency: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    """
    Login success ke baad yeh return hoga.
    access_token = short lived (30 min) — API calls ke liye
    refresh_token = long lived (7 days) — naya access token lene ke liye
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds mein
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    """Refresh token se naya access token lene ke liye."""
    refresh_token: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    currency: Optional[str] = Field(None, max_length=10)

class PasswordChange(BaseModel):
    """Password change karne ke liye."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)