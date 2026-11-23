# Pinned base image (never "latest"): Python 3.12, slim Debian Bookworm
FROM python:3.12.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 1) Dependencies first: this layer is cached until requirements.txt changes
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2) Unprivileged user for running the app
RUN useradd --create-home --uid 10001 appuser

# 3) Application code last: code edits rebuild only from here
COPY --chown=appuser:appuser alembic.ini ./
COPY --chown=appuser:appuser alembic ./alembic
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser docker-entrypoint.sh ./

USER appuser

EXPOSE 8000

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]
