# Mental Math Gym

A self-hosted app for practicing mental arithmetic. Pick a lesson, set how many
problems you want, and work through a timed drill in the browser. The app
tracks every attempt so you can see how you're improving over time and retry
the problems you missed.

## Features

- **Practice Gym** — choose a lesson (times tables, addition, subtraction,
  etc.), tune its parameters, set the problem count, and start a timed
  session. Two retry modes are supported:
  - *Retry*: wrong answers loop back until you get them right.
  - *Advance*: move on after each attempt, revisit misses at the end.
- **Progress Tracker** — browse progress by Unit → Lesson, see score-over-time
  charts, and drill into any past session for a per-problem review.
- **Retry Missed** — turn the problems you got wrong in a completed session
  into a fresh session with one click.
- **Strict numeric input** and an optional per-problem timer.
- Runs entirely locally with `docker compose up`. Your data lives in a local
  SQLite database — nothing leaves your machine.

## Problems

Problems have been taken from the following sources:

* Basics such as times tables, addition and subtraction
* ["Mental Math in the Middle Grades"](https://www.amazon.com/Mental-Middle-Grades-Blackline-Masters/dp/0866513124), Blackline Masters. Hope and Reyes, 1990


## Quick start

Requires Docker + Docker Compose.

```sh
git clone <this-repo>
cd mental_math_gym
docker compose up
```

Then open <http://localhost:8050> in a browser.

- `docker compose down` — stop the stack (keeps your practice history).
- `docker compose down -v` — stop and wipe the database volume.

---

## Developer notes

### Architecture

| Layer | Tech |
| --- | --- |
| Problem generation | Plain Python classes in `mathgen/` |
| API | FastAPI (`backend/app/`) |
| Persistence | SQLite via SQLAlchemy 2.0 + Alembic migrations |
| Frontend | Vanilla JS ES modules, pico.css classless, Chart.js (served as static files by FastAPI) |
| Packaging | Docker + Docker Compose for local dev |

Request path: browser → FastAPI `/api/v1/*` → service layer
(`backend/app/services/`) → SQLAlchemy models → SQLite. Static frontend is
mounted at `/` and falls through to the API routes.

### Repository layout

```
mathgen/            # problem generators, grouped by lesson
  common/           # Problem, ProblemSetBaseClass, registry
  lessons/          # basic.py, mmmg.py, ...
backend/
  app/
    api/v1/         # FastAPI routers (lessons, sessions)
    schemas/        # Pydantic DTOs
    services/       # session_service, stats_service
    db/             # models, migrations
    config.py, main.py, logging.py
  tests/            # pytest + httpx tests
frontend/
  index.html
  js/               # router, state, api, views/
  css/
Dockerfile
docker-compose.yml
alembic.ini
pyproject.toml
```

### Local development (Docker)

`docker compose up` builds the image on first run, applies migrations, then
serves uvicorn with `--reload`. `backend/`, `frontend/`, and `mathgen/` are
bind-mounted, so edits take effect without rebuilding. `PYTHONPATH=/app`
ensures the bind-mount (not the pip-installed copy in `site-packages`) is
imported.

The SQLite database lives in the `mmg_data` named volume at `/app/data/mmg.db`
inside the container.

### Local development (without Docker)

```sh
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn backend.app.main:app --reload --port 8050
```

### Running tests

```sh
# inside the container
docker compose run --rm app sh -c "pip install --quiet pytest httpx && pytest backend/tests -q"

# or on the host, with the dev extras installed
pytest backend/tests -q
```

### Adding a new lesson

1. Create (or extend) a file under `mathgen/lessons/`.
2. Define a class that subclasses `ProblemSetBaseClass` and implements
   `new_problem()` returning a `Problem(answer, inputs, prompt)`.
3. Decorate it with `@register_lesson(id=..., title=..., unit=..., params=(...))`.
   Declared `LessonParam`s are what the frontend renders in the setup form.
4. Make sure the module is imported by `mathgen/lessons/__init__.py` so the
   registry discovers it at startup.

No backend changes are required — lessons are picked up via the registry and
exposed through `/api/v1/lessons`.

### Configuration

Environment variables (see `backend/app/config.py`):

| Var | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./mmg.db` | SQLAlchemy URL |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `APP_ENV` | `local` | Informational tag |
| `FRONTEND_DIR` | `frontend` | Path served as static files; missing dir is tolerated (useful for tests) |

### Conventions

- Use the centralized logger (`backend.app.logging.get_logger(__name__)`)
  rather than the root logger.
- Create a new branch before making changes; merge back via PR/merge commit.
- SQLAlchemy sessions come from `backend.app.deps.get_db` — don't instantiate
  sessions ad-hoc in route handlers.

Sonnet 4.6 using Claude Code was used in the making of this project.