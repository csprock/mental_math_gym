from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from backend.app.config import get_settings
from backend.app.logging import get_logger, setup_logging

_settings = get_settings()
setup_logging(_settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    import mathgen.lessons  # noqa: F401  triggers lesson discovery
    from mathgen.common.registry import get_registry

    registry = get_registry()
    logger.info("registered %d lessons: %s", len(registry.all()), registry.ids())
    yield


app = FastAPI(title="Mental Math Gym", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
