# ==============================================================================
# GearWitness Container Definition
# Multi-stage build: Frontend Vite assets + Python FastAPI Backend
# ==============================================================================

# Stage 1: Build React/TypeScript Frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python Runtime
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_MODE=fixture \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Install minimal system dependencies for OpenCV and healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user and application directories with proper ownership
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copy application source code and bundled fixtures
COPY backend/ ./backend/
COPY data/ ./data/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Ensure writable paths for SQLite, uploads, and media with appuser ownership
RUN mkdir -p /app/uploads/originals /app/uploads/derived /app/uploads/crops /app/uploads/diffs \
             /app/backend/data/media /app/backend/data/fixtures \
    && touch /app/gearwitness.db \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# HTTP health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]
