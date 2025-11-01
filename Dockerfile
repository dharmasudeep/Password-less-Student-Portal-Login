FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/
RUN pip install --upgrade pip && pip install --no-cache-dir .[dev]

COPY . /app

RUN useradd -m appuser
USER appuser

ENV FLASK_APP=app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
