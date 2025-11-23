FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1
WORKDIR /app

# System dependencies for building wheels (uvloop/httptools)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt

# Runtime image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && adduser --disabled-password --gecos "" appuser \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request, sys; \
  import contextlib; \
  try: \
    with urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3) as resp: \
      sys.exit(0 if resp.status < 400 else 1); \
  except Exception: \
    sys.exit(1)"

USER appuser

CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\", \"--workers\", \"4\"]
