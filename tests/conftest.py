import os
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base, get_db
from db.models.user import User
from server import app
from utils.auth import get_password_hash

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/atlys_test"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables once for entire test session"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Fresh transaction for each test, rolled back after"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db, monkeypatch):
    """Test client with database override for both get_db and get_db_context"""

    def override_get_db():
        yield db

    @contextmanager
    def override_get_db_context():
        yield db

    # Patch get_db_context used by middleware
    monkeypatch.setattr(
        "middlewares.jwt_auth_middleware.get_db_context",
        override_get_db_context,
    )

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_member(db):
    """Create a test member user"""
    user = User(
        email="member@test.com",
        password=get_password_hash("testpass"),
        role="member",
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def test_manager(db):
    """Create a test manager user"""
    user = User(
        email="manager@test.com",
        password=get_password_hash("testpass"),
        role="manager",
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def test_admin(db):
    """Create a test admin user"""
    user = User(
        email="admin@test.com",
        password=get_password_hash("testpass"),
        role="admin",
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def member_headers(client, test_member):
    """Auth headers for member user"""
    response = client.post(
        "/auth/login",
        json={"email": "member@test.com", "password": "testpass"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def manager_headers(client, test_manager):
    """Auth headers for manager user"""
    response = client.post(
        "/auth/login",
        json={"email": "manager@test.com", "password": "testpass"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, test_admin):
    """Auth headers for admin user"""
    response = client.post(
        "/auth/login",
        json={"email": "admin@test.com", "password": "testpass"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
