import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.main import create_app
from app.db.session import get_session
# Import all models to ensure they are registered with SQLModel
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.card import Card
from app.models.statement import Statement


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session backed by a temp SQLite file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        engine = create_engine(
            f"sqlite:///{path}",
            connect_args={"check_same_thread": False},
            echo=False,
        )
        SQLModel.metadata.create_all(engine)

        with Session(engine) as session:
            yield session
    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with dependency override using the temp DB session."""
    def get_session_override():
        # Match the original dependency shape by yielding a session
        yield session

    app = create_app()
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()
