"""
FastAPI application entry point.
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.scheduler import setup_scheduler, shutdown_scheduler
from app.api.opportunities import router as opportunities_router
from app.api.applications import router as applications_router

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info(f"Starting Opportunity Tracker API (env={settings.APP_ENV})")

    # Initialize database tables
    await init_db()

    # Start the daily scheduler
    if settings.APP_ENV != "test":
        setup_scheduler()

    yield

    # Shutdown
    shutdown_scheduler()
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="Global Opportunity Tracker API",
    description=(
        "Automated AI-powered system that discovers, tracks, and categorizes "
        "global opportunities for students, founders, researchers, and creators."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=True,
)

# CORS — allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(opportunities_router)
app.include_router(applications_router)


@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {
        "status": "healthy",
        "env": settings.APP_ENV,
        "version": "1.0.0",
    }


@app.get("/", tags=["system"])
async def root():
    return {
        "message": "Global Opportunity Tracker API",
        "docs": "/docs",
        "health": "/health",
    }
