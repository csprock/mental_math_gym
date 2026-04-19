from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from typing import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.db.base import Base
from backend.app.db import models  # noqa: F401  register models on Base.metadata


@pytest.fixture()
def db_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
