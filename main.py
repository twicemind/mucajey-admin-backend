"""
mucajey Admin Backend - FastAPI
Verwaltungsoberfläche für Hitster Cards Management
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from routers import cards, files, failed_searches, imports, statistics
from config import settings

# FastAPI App
app = FastAPI(
    title="mucajey Admin API",
    description="Admin-Backend für mucajey Hitster Cards Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mucajey Admin API",
        "version": "1.0.0"
    }

# Include Routers
app.include_router(cards.router, prefix="/api/cards", tags=["Cards"])
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(failed_searches.router, prefix="/api/failed-searches", tags=["Failed Searches"])
app.include_router(imports.router, prefix="/api/import", tags=["Import Tools"])
app.include_router(statistics.router, prefix="/api/stats", tags=["Statistics"])

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
