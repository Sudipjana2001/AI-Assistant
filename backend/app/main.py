"""
Market Research Multi-Agent System - FastAPI Backend
Using Azure AI Foundry SDK
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print(f"Starting {settings.PROJECT_NAME}...")
    
    # Initialize agent registry
    try:
        from agents.registry import AgentRegistry
        AgentRegistry.initialize()
        print("Agent registry initialized")
    except Exception as e:
        print(f"Warning: Could not initialize agents: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-Agent Market Research Assistant API with Azure AI Foundry",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for frontend
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
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Market Research Multi-Agent API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
