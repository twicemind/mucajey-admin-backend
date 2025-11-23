# mucajey-admin-backend

Production-ready FastAPI Admin Backend container.

## Docker
```bash
# Build optimized, non-root image
docker build -t mucajey-admin-backend:latest .

# Run (exposes 8000, optional env overrides from .env)
docker run --rm -p 8000:8000 --env-file .env mucajey-admin-backend:latest
```

- Healthcheck: `GET /health`
- Default host/port: `0.0.0.0:8000`
- CORS origins and API URLs configurable via `.env` (see `config.py`)

## Stack
- FastAPI + Uvicorn
- Python 3.11-slim base
- Multi-stage build with wheel caching, security headers handled by app
