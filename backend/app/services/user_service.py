# app/services/user_service.py — poora replace karo
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, PasswordChange
from app.core.security import hash_password, verify_password
import uuid

class UserService:

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Naya user register karo."""
        existing = db.query(User).filter(
            User.email == user_data.email.lower()
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already registered. Please login."
            )

        user = User(
            id=uuid.uuid4(),
            email=user_data.email.lower(),  # Always lowercase store karo
            full_name=user_data.full_name.strip(),
            hashed_password=hash_password(user_data.password),
            currency=user_data.currency.upper()
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """Email aur password verify karo."""
        user = db.query(User).filter(
            User.email == email.lower()
        ).first()

        # Dono cases mein same error — security ke liye
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account disabled. Contact support."
            )

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        """ID se user dhundho."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    @staticmethod
    def update_profile(
        db: Session,
        user: User,
        update_data: UserUpdate
    ) -> User:
        """Profile update karo — sirf jo fields bheje hain unhe update karo."""
        update_dict = update_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(
        db: Session,
        user: User,
        password_data: PasswordChange
    ) -> None:
        """Password change karo."""
        # Pehle current password verify karo
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Naya password hash karke save karo
        user.hashed_password = hash_password(password_data.new_password)
        db.commit()