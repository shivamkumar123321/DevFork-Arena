"""
API Routes module for DevFork Arena.

Contains all FastAPI routers for different endpoints.
"""

from .competitions import router as competitions_router

__all__ = [
    "competitions_router",
]
