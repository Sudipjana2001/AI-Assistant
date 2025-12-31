"""
API v1 Router
Combines all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import health, files, agents, chat, databricks

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(databricks.router, prefix="/databricks", tags=["Databricks"])
