FROM python:3.10-alpine

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY mathgen /app/mathgen
COPY backend /app/backend

RUN pip install --no-cache-dir /app

EXPOSE 8050

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8050"]
