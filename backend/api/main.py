"""
gCite Backend API
FastAPI application for intelligent citation search
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from .models import HealthResponse, RootResponse
from .routes import router
from config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="gCite API",
    description="Intelligent citation search with AI filtering",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

# Logging setup
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.get("/", response_model=RootResponse)
async def root():
    """Root endpoint with service information."""
    return RootResponse(
        service="gCite API",
        version="0.1.0",
        status="operational"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=time.time()
    )


@app.middleware("http")
async def log_requests(request, call_next):
    """Log all HTTP requests."""
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.2f}ms "
        f"with status {response.status_code}"
    )

    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
