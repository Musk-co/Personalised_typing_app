"""
FastAPI application entry point.
Sets up routes, middleware, and core dependencies.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import auth, sessions, users, analytics, adapter, keystrokes, skill_profile, exercises, progress
from app.db.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle context manager.
    Handles startup and shutdown logic.
    """
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")
    yield
    # Shutdown
    print("🛑 Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A scalable, ML-ready typing trainer API",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.api_prefix, tags=["auth"])
app.include_router(sessions.router, prefix=settings.api_prefix, tags=["sessions"])
app.include_router(users.router, prefix=settings.api_prefix, tags=["users"])
app.include_router(analytics.router, prefix=settings.api_prefix, tags=["analytics"])
app.include_router(adapter.router, prefix=settings.api_prefix, tags=["adapter"])
app.include_router(keystrokes.router, tags=["keystroke-recording"])
app.include_router(skill_profile.router, tags=["skill-profile"])
app.include_router(exercises.router, tags=["exercises"])
app.include_router(progress.router, tags=["progress"])


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "adapter": settings.adapter_type,
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "features": {
            "real_time_feedback": settings.enable_real_time_feedback,
            "analytics": settings.enable_analytics,
            "leaderboard": settings.enable_leaderboard,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
    )
