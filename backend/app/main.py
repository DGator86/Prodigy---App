"""
CrossFit Performance API - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .db.database import init_db
from .api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    init_db()
    yield
    # Shutdown (if needed)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## CrossFit Performance API
    
    A physics-based performance measurement system for CrossFit athletes.
    
    ### Features
    - **EWU (Effective Work Units)**: Standardized work accounting across modalities
    - **Density Power**: Work rate metrics (EWU/min)
    - **Repeatability**: Drift and spread analysis
    - **Athlete Completeness**: 5-domain radar chart
    - **Confidence Scoring**: Accuracy improves with more data
    
    ### Domains
    1. Strength Output
    2. Monostructural Output
    3. Mixed-Modal Capacity
    4. Sprint/Power Capacity
    5. Repeatability
    """,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api": settings.API_V1_PREFIX
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
