from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.api.v1 import lessons as lessons_router
from backend.app.api.v1 import sessions as sessions_router
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

v1 = APIRouter(prefix="/api/v1")
v1.include_router(lessons_router.router)
v1.include_router(sessions_router.router)
app.include_router(v1)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Static frontend. Mount last so /api/v1/* and /health still win. Missing dir
# is tolerated so tests that run from a bare source checkout don't break.
_frontend_path = Path(_settings.frontend_dir)
if _frontend_path.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=_frontend_path, html=True),
        name="frontend",
    )
    logger.info("serving frontend from %s", _frontend_path.resolve())
else:
    logger.info("frontend dir %s not found; skipping static mount", _frontend_path)
