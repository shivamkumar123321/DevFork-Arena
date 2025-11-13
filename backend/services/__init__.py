"""
Services module for DevFork Arena.

High-level services that orchestrate business logic and coordinate
between agents, database, and other components.
"""

from .competition_service import (
    CompetitionService,
    CompetitionServiceError,
    create_competition_service
)

__all__ = [
    "CompetitionService",
    "CompetitionServiceError",
    "create_competition_service",
]

__version__ = "1.0.0"
