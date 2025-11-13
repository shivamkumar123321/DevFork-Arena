"""
Competition API Routes

FastAPI routes for managing competitions, starting competitions,
and retrieving competition results.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import asyncio
import logging

from models import (
    CompetitionResponse,
    CompetitionResults,
    CompetitionStatus,
    ChallengeResponse,
    SubmissionResponse
)
from services import CompetitionService, CompetitionServiceError, create_competition_service
from database import db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/competitions",
    tags=["competitions"],
    responses={404: {"description": "Competition not found"}},
)

# Global service instance (will be initialized with database in production)
competition_service = create_competition_service(database=db)


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateCompetitionRequest(BaseModel):
    """Request model for creating a new competition."""
    challenge_id: str
    agent_ids: List[UUID]
    name: Optional[str] = None
    description: Optional[str] = None
    timeout_per_agent: int = Field(default=300, description="Timeout in seconds (default: 5 minutes)")


class StartCompetitionResponse(BaseModel):
    """Response model for starting a competition."""
    competition_id: UUID
    status: str
    message: str
    started_at: datetime
    expected_duration_seconds: int
    tracking_url: str


class CompetitionStatusResponse(BaseModel):
    """Response model for competition status."""
    competition_id: UUID
    status: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    challenge_id: str
    agent_count: int
    winner: Optional[UUID] = None
    error_message: Optional[str] = None


# ============================================================================
# Competition Endpoints
# ============================================================================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_competition(
    challenge_id: str,
    agent_ids: List[UUID],
    name: Optional[str] = None,
    description: Optional[str] = None
) -> CompetitionResponse:
    """
    Create a new competition.

    Creates a competition between multiple agents on a specific challenge.
    The competition will be in 'pending' status until started.

    Args:
        challenge_id: ID of the challenge to compete on
        agent_ids: List of agent UUIDs to participate
        name: Optional competition name
        description: Optional competition description

    Returns:
        CompetitionResponse with competition details

    Raises:
        HTTPException: If creation fails
    """
    try:
        logger.info(f"Creating competition for challenge {challenge_id} with {len(agent_ids)} agents")

        if len(agent_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 2 agents are required for a competition"
            )

        competition = await competition_service.create_competition(
            challenge_id=challenge_id,
            agent_ids=agent_ids,
            name=name,
            description=description
        )

        logger.info(f"Competition {competition.id} created successfully")
        return competition

    except ValueError as e:
        logger.error(f"Invalid competition data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create competition: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create competition: {str(e)}"
        )


@router.post("/{competition_id}/start")
async def start_competition(
    competition_id: UUID,
    background_tasks: BackgroundTasks,
    timeout_per_agent: int = 300
) -> StartCompetitionResponse:
    """
    Start a competition - all agents will attempt the challenge.

    This endpoint starts a pending competition and returns immediately.
    The competition runs in the background, and you can track progress
    using the status endpoint.

    Args:
        competition_id: UUID of the competition to start
        background_tasks: FastAPI background tasks (injected)
        timeout_per_agent: Maximum time in seconds for each agent (default: 300)

    Returns:
        StartCompetitionResponse with competition status and tracking info

    Raises:
        HTTPException: If competition not found or cannot be started
    """
    try:
        logger.info(f"Starting competition {competition_id}")

        # Verify competition exists and is in pending status
        competition = await competition_service.get_competition_status(competition_id)

        if not competition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Competition {competition_id} not found"
            )

        if competition.status != CompetitionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Competition is already {competition.status.value}. Only pending competitions can be started."
            )

        # Start competition in background
        background_tasks.add_task(
            _run_competition_background,
            competition_id,
            timeout_per_agent
        )

        # Calculate expected duration
        expected_duration = len(competition.agent_ids) * timeout_per_agent

        logger.info(
            f"Competition {competition_id} started with {len(competition.agent_ids)} agents. "
            f"Expected duration: {expected_duration}s"
        )

        return StartCompetitionResponse(
            competition_id=competition_id,
            status="running",
            message="Competition started successfully. Agents are now competing.",
            started_at=datetime.utcnow(),
            expected_duration_seconds=expected_duration,
            tracking_url=f"/api/competitions/{competition_id}/status"
        )

    except HTTPException:
        raise
    except CompetitionServiceError as e:
        logger.error(f"Competition service error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to start competition: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start competition: {str(e)}"
        )


@router.get("/{competition_id}/status")
async def get_competition_status(competition_id: UUID) -> CompetitionStatusResponse:
    """
    Get the current status of a competition.

    Returns the current state of the competition including status,
    timestamps, and winner (if completed).

    Args:
        competition_id: UUID of the competition

    Returns:
        CompetitionStatusResponse with current status

    Raises:
        HTTPException: If competition not found
    """
    try:
        competition = await competition_service.get_competition_status(competition_id)

        if not competition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Competition {competition_id} not found"
            )

        return CompetitionStatusResponse(
            competition_id=competition.id,
            status=competition.status.value,
            created_at=competition.created_at,
            started_at=competition.started_at,
            completed_at=competition.completed_at,
            challenge_id=competition.challenge_id,
            agent_count=len(competition.agent_ids),
            winner=competition.winner,
            error_message=competition.error_message if hasattr(competition, 'error_message') else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get competition status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get competition status: {str(e)}"
        )


@router.get("/{competition_id}/results")
async def get_competition_results(competition_id: UUID) -> CompetitionResults:
    """
    Get the complete results of a competition.

    Returns detailed results including leaderboard, submissions,
    and performance metrics. Only available for completed competitions.

    Args:
        competition_id: UUID of the competition

    Returns:
        CompetitionResults with full details

    Raises:
        HTTPException: If competition not found or not completed
    """
    try:
        # Check if competition exists and is completed
        competition = await competition_service.get_competition_status(competition_id)

        if not competition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Competition {competition_id} not found"
            )

        if competition.status != CompetitionStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Competition is {competition.status.value}. Results are only available for completed competitions."
            )

        # Fetch results
        results = await competition_service.get_competition_results(competition_id)

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Results not found for competition {competition_id}"
            )

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get competition results: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get competition results: {str(e)}"
        )


@router.get("/{competition_id}/leaderboard")
async def get_competition_leaderboard(competition_id: UUID) -> List[dict]:
    """
    Get the leaderboard for a competition.

    Returns the ranked list of agents and their scores.
    Available for completed competitions.

    Args:
        competition_id: UUID of the competition

    Returns:
        List of leaderboard entries

    Raises:
        HTTPException: If competition not found or not completed
    """
    try:
        results = await get_competition_results(competition_id)
        return results.leaderboard

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get leaderboard: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get leaderboard: {str(e)}"
        )


@router.get("/{competition_id}/submissions")
async def get_competition_submissions(
    competition_id: UUID,
    agent_id: Optional[UUID] = None
) -> List[SubmissionResponse]:
    """
    Get submissions from a competition.

    Returns all submissions, optionally filtered by agent.

    Args:
        competition_id: UUID of the competition
        agent_id: Optional agent UUID to filter submissions

    Returns:
        List of submissions

    Raises:
        HTTPException: If competition not found
    """
    try:
        results = await competition_service.get_competition_results(competition_id)

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Results not found for competition {competition_id}"
            )

        submissions = results.submissions

        # Filter by agent if specified
        if agent_id:
            submissions = [s for s in submissions if s.agent_id == agent_id]

        return submissions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get submissions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get submissions: {str(e)}"
        )


@router.delete("/{competition_id}")
async def cancel_competition(competition_id: UUID) -> dict:
    """
    Cancel a running competition.

    Stops a competition that is currently running.

    Args:
        competition_id: UUID of the competition to cancel

    Returns:
        Confirmation message

    Raises:
        HTTPException: If competition not found or cannot be cancelled
    """
    try:
        success = await competition_service.cancel_competition(competition_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Competition cannot be cancelled. It may not be running."
            )

        return {
            "message": "Competition cancelled successfully",
            "competition_id": str(competition_id)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel competition: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel competition: {str(e)}"
        )


@router.get("/")
async def list_competitions(
    status: Optional[str] = None,
    challenge_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[CompetitionStatusResponse]:
    """
    List competitions with optional filtering.

    Args:
        status: Filter by status (pending, running, completed, failed)
        challenge_id: Filter by challenge ID
        limit: Maximum number of results (default: 50)
        offset: Number of results to skip (default: 0)

    Returns:
        List of competition status responses
    """
    # TODO: Implement database query in Step 5
    # For now, return empty list
    logger.warning("List competitions not yet implemented - requires database")
    return []


# ============================================================================
# Background Tasks
# ============================================================================

async def _run_competition_background(competition_id: UUID, timeout_per_agent: int):
    """
    Background task to run a competition.

    This runs the competition asynchronously and handles any errors.

    Args:
        competition_id: UUID of the competition to run
        timeout_per_agent: Maximum time per agent in seconds
    """
    try:
        logger.info(f"Background task: Running competition {competition_id}")

        results = await competition_service.run_competition(
            competition_id=competition_id,
            timeout_per_agent=timeout_per_agent
        )

        logger.info(
            f"Background task: Competition {competition_id} completed. "
            f"Winner: {results.winner}, Duration: {results.total_duration:.2f}s"
        )

    except CompetitionServiceError as e:
        logger.error(
            f"Background task: Competition {competition_id} failed: {e}",
            exc_info=True
        )
    except Exception as e:
        logger.error(
            f"Background task: Unexpected error in competition {competition_id}: {e}",
            exc_info=True
        )


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def competition_health() -> dict:
    """
    Health check for competition service.

    Returns:
        Service health status and statistics
    """
    try:
        stats = competition_service.get_statistics()
        return {
            "status": "healthy",
            "service": "competition",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Competition health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "competition",
            "error": str(e)
        }
