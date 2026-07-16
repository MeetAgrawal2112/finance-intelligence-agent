import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, String, TypeDecorator, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import UUID as PyUUID
import uuid

# ── UUID type for SQLite ───────────────────────────────────────────────────────
class UUIDString(TypeDecorator):
    """SQLite ke liye UUID → String conversion."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return PyUUID(str(value))
        except (ValueError, AttributeError):
            return value

# PostgreSQL UUID ko replace karo SQLite compatible version se
from sqlalchemy.dialects import postgresql
postgresql.UUID = UUIDString

# ── Test DB setup ──────────────────────────────────────────────────────────────
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User
from app.models.category import Category
from app.core.security import hash_password

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    categories = [
        Category(id=uuid.uuid4(), name="Groceries",
                 icon="🛒", color="#4CAF50", is_system=True),
        Category(id=uuid.uuid4(), name="Dining Out",
                 icon="🍕", color="#FF5722", is_system=True),
        Category(id=uuid.uuid4(), name="Transport",
                 icon="🚗", color="#FF9800", is_system=True),
        Category(id=uuid.uuid4(), name="Salary",
                 icon="💰", color="#8BC34A", is_system=True),
    ]
    for cat in categories:
        db.add(cat)

    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password=hash_password("testpassword123"),
        currency="INR",
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_transaction_data():
    return {
        "amount": 500.0,
        "transaction_type": "debit",
        "description": "Zomato food order",
        "merchant_name": "Zomato",
        "transaction_date": "2026-01-15T12:00:00Z",
        "currency": "INR",
    }
