"""
Shared pytest fixtures for WARMS-Backend tests.

Strategy
--------
* Use SQLite (in-memory) so tests never touch the real PostgreSQL database.
* Override the FastAPI dependency `getDb` to inject the test session.
* Provide ready-made JWT tokens for visitor / ranger / admin roles so
  individual tests don't have to go through the full signup → login flow
  unless they explicitly want to test those endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── engine & session ──────────────────────────────────────────────────────────
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── import app *after* setting env vars so DB_* vars don't break at import ───
import os
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("SECRET_KEY", "testsecretkey")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from main import app
from src.db.db import Base, getDb
from src.auth.auth import get_password_hash, create_access_token
from src.models.userModel import User


def _override_get_db():
    """Yield a test-scoped SQLite session instead of the real PostgreSQL one."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[getDb] = _override_get_db


# ── session-scoped DB setup / teardown ───────────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create all tables once per test session, drop them when done."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ── function-scoped clean DB state ───────────────────────────────────────────
@pytest.fixture(autouse=True)
def clean_db():
    """Wipe all table rows before every test so tests are independent."""
    yield
    db = TestingSessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()


# ── TestClient ────────────────────────────────────────────────────────────────
@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# ── helper: create a user directly in the DB ─────────────────────────────────
def _make_user(role: str, username: str, email: str, password: str = "password123") -> User:
    db = TestingSessionLocal()
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role=role,
        is_active=True,
        is_locked=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def _token_for(user: User) -> str:
    return create_access_token(data={"sub": user.email, "role": user.role.value})


# ── role fixtures ─────────────────────────────────────────────────────────────
@pytest.fixture
def visitor_user():
    return _make_user("user", "visitor1", "visitor@test.com")


@pytest.fixture
def ranger_user():
    return _make_user("ranger", "ranger1", "ranger@test.com")


@pytest.fixture
def admin_user():
    return _make_user("admin", "admin1", "admin@test.com")


@pytest.fixture
def visitor_token(visitor_user):
    return _token_for(visitor_user)


@pytest.fixture
def ranger_token(ranger_user):
    return _token_for(ranger_user)


@pytest.fixture
def admin_token(admin_user):
    return _token_for(admin_user)


# ── auth header helpers ───────────────────────────────────────────────────────
@pytest.fixture
def visitor_headers(visitor_token):
    return {"Authorization": f"Bearer {visitor_token}"}


@pytest.fixture
def ranger_headers(ranger_token):
    return {"Authorization": f"Bearer {ranger_token}"}


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
