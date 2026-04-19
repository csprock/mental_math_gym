from __future__ import annotations

from typing import Iterator

from sqlalchemy.orm import Session

from backend.app.db.base import SessionLocal


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
