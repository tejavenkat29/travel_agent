# syntax=docker/dockerfile:1
# ----------------------------------------------------------------------------
# AI Multi-Agent Travel Planner — production image (multi-stage)
# ----------------------------------------------------------------------------

# --- Stage 1: builder — compile/install dependencies into a venv ------------
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Build tools needed to compile wheels (e.g. asyncpg). Not carried to runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Self-contained virtualenv we can copy wholesale to the runtime image.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt


# --- Stage 2: runtime — slim image with only the venv + app code ------------
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy the prebuilt dependencies (no compilers in the final image).
COPY --from=builder /opt/venv /opt/venv

# Copy application source (respecting .dockerignore).
COPY . .

# Run as a non-root user for security.
RUN useradd --create-home --uid 1000 appuser \
    && chmod +x docker/entrypoint.sh \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Container-level liveness check hitting the app's health endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

ENTRYPOINT ["docker/entrypoint.sh"]
