"""
FastAPI application for AI Content Agents service.

This module defines the main FastAPI application with routing,
middleware, and configuration for the content generation API.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Any, Dict
import logging
from datetime import datetime

# Import routers
from api.routes import blog_router, social_router, amazon_router, competitor_router, tiktok_scheduling_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="AI Content Agents API",
    description="REST API for AI-powered content generation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(blog_router, prefix="/api")
app.include_router(social_router, prefix="/api")
app.include_router(amazon_router, prefix="/api")
app.include_router(competitor_router, prefix="/api")
app.include_router(tiktok_scheduling_router, prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for uncaught exceptions.

    Args:
        request: The incoming request
        exc: The exception that was raised

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )


@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint - API information.

    Returns:
        Dict containing API metadata
    """
    return {
        "service": "AI Content Agents API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Dict containing health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "ai-content-agents"
    }


@app.on_event("startup")
async def startup_event() -> None:
    """
    Application startup event handler.

    Performs initialization tasks when the application starts.
    """
    logger.info("AI Content Agents API starting up...")
    logger.info("FastAPI application initialized successfully")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Application shutdown event handler.

    Performs cleanup tasks when the application shuts down.
    """
    logger.info("AI Content Agents API shutting down...")
    logger.info("Cleanup completed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
