"""
API v1 routes.
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .workouts import router as workouts_router
from .domains import router as domains_router, trends_router
from .exports import router as exports_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(workouts_router)
api_router.include_router(domains_router)
api_router.include_router(exports_router)
