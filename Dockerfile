# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user --no-cache-dir --no-warn-script-location -r requirements.txt

FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN groupadd -r app && useradd -r -g app -s /bin/false app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH=/home/app/.local/bin:$PATH \
    PYTHONHASHSEED=random \
    UPLOAD_DIR=/tmp/uploads

WORKDIR /app

COPY --from=builder /root/.local /home/app/.local

COPY --chown=app:app . .

RUN chown -R app:app /app \
    && chmod -R 755 /app \
    && find /app -type f -name "*.py" -exec chmod 644 {} \; \
    && mkdir -p /tmp/uploads \
    && chown app:app /tmp/uploads \
    && chmod 755 /tmp/uploads

USER app

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

LABEL org.opencontainers.image.title="Suggestion Box" \
      org.opencontainers.image.description="Anonymous suggestion box API" \
      org.opencontainers.image.vendor="DSO Course"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
