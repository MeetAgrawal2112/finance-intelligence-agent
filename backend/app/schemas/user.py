from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from pydantic import field_validator
import re
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=100)
    currency: str = Field(default="INR", max_length=10)

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        """
        Strong password enforce karo:
        - Min 8 characters
        - At least 1 uppercase
        - At least 1 lowercase
        - At least 1 digit
        """
        if len(v) < 8:
            raise ValueError('Password minimum 8 characters hona chahiye')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password mein kam se kam 1 uppercase letter chahiye')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password mein kam se kam 1 lowercase letter chahiye')
        if not re.search(r'\d', v):
            raise ValueError('Password mein kam se kam 1 number chahiye')
        return v

    @field_validator('full_name')
    @classmethod
    def name_no_special_chars(cls, v):
        from app.core.validators import check_xss
        if check_xss(v):
            raise ValueError('Invalid characters in name')
        return v.strip()
    
    
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
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    currency: Optional[str] = Field(None, max_length=10)

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)