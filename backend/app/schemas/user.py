# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    """
    Registration ke time frontend se yeh data aayega.
    EmailStr automatically email format validate karta hai.
    """
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=100)
    currency: str = Field(default="INR", max_length=10)

class UserLogin(BaseModel):
    """Login ke time yeh data aayega."""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """
    API response mein user data — password kabhi nahi bhejenge!
    orm_mode=True matlab SQLAlchemy model directly
    is schema mein convert ho sakta hai.
    """
    id: UUID
    email: str
    full_name: str
    currency: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    """Login success ke baad yeh return hoga."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserUpdate(BaseModel):
    """Profile update ke liye — sab fields optional hain."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    currency: Optional[str] = Field(None, max_length=10)