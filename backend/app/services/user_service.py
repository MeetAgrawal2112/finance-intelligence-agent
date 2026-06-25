# app/services/user_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password, create_access_token
import uuid

class UserService:

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Naya user register karo.
        Pehle check karo email already exist karta hai ya nahi.
        """
        # Duplicate email check
        existing = db.query(User).filter(
            User.email == user_data.email
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Password hash karo — kabhi plain text store mat karo
        hashed = hash_password(user_data.password)

        user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed,
            currency=user_data.currency
        )

        db.add(user)
        db.commit()
        db.refresh(user)  # DB se fresh data lo (auto-generated fields ke liye)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """
        Login — email aur password verify karo.
        """
        user = db.query(User).filter(User.email == email).first()

        # Security tip: dono cases mein same error do
        # Agar "email not found" alag error de toh attacker
        # pata kar sakta hai kaunse emails registered hain
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        """User ID se user dhundho."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user