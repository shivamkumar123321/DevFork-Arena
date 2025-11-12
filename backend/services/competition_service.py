"""
Competition Runner Service

High-level service that orchestrates the entire competition flow:
- Updates competition status (pending → running → completed)
- Runs all agents in parallel using AgentManager
- Collects and compares results
- Determines winner
- Updates leaderboard and database

This service wraps the AgentManager and adds database persistence,
status management, and error handling.
"""
import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from models import (
    CompetitionResponse,
    CompetitionResults,
    CompetitionStatus,
    ChallengeResponse,
    SubmissionResponse
)
from agents import AgentManager, AgentExecutionError

logger = logging.getLogger(__name__)


class CompetitionServiceError(Exception):
    """Base exception for competition service errors."""
    pass


class CompetitionService:
    """
    High-level service for managing competitions.

    This service orchestrates the entire competition lifecycle:
    1. Fetches competition details from database
    2. Updates status to "running"
    3. Loads all participating agents
    4. Executes agents concurrently on the challenge
    5. Collects all submissions
    6. Determines winner (highest score, fastest time)
    7. Updates competition with winner
    8. Sets status to "completed"

    Example:
        ```python
        service = CompetitionService(database=db)

        # Run a competition
        results = await service.run_competition(
            competition_id=competition_id
        )

        print(f"Winner: {results.winner}")
        for entry in results.leaderboard:
            print(f"#{entry['rank']}: Score {entry['score']}")
        ```
    """

    def __init__(self, database=None):
        """
        Initialize the competition service.

        Args:
            database: Database connection/pool (optional, will be implemented in Step 5)
        """
        self.database = database
        self.agent_manager = AgentManager(database=database)
        logger.info("CompetitionService initialized")

    async def run_competition(
        self,
        competition_id: UUID,
        timeout_per_agent: int = 300
    ) -> CompetitionResults:
        """
        Run a complete competition orchestration.

        This is the main entry point for running competitions. It handles:
        - Loading competition and challenge data
        - Status management
        - Agent execution
        - Winner determination
        - Database persistence

        Args:
            competition_id: UUID of the competition to run
            timeout_per_agent: Maximum time in seconds for each agent

        Returns:
            CompetitionResults with leaderboard, winner, and all submissions

        Raises:
            CompetitionServiceError: If competition cannot be run
        """
        logger.info(f"Starting competition {competition_id}")

        try:
            # Step 1: Fetch competition details from DB
            competition = await self._fetch_competition(competition_id)

            if competition.status == CompetitionStatus.COMPLETED:
                logger.warning(f"Competition {competition_id} is already completed")
                raise CompetitionServiceError(
                    f"Competition {competition_id} is already completed"
                )

            # Fetch challenge details
            challenge = await self._fetch_challenge(competition.challenge_id)

            # Step 2: Update status to "running"
            await self._update_competition_status(
                competition_id,
                CompetitionStatus.RUNNING,
                started_at=datetime.utcnow()
            )

            logger.info(
                f"Competition {competition_id} started with "
                f"{len(competition.agent_ids)} agents on challenge '{challenge.title}'"
            )

            # Steps 3-5: Load agents, execute concurrently, collect submissions
            # (Delegated to AgentManager)
            results = await self.agent_manager.run_competition(
                competition_id=competition_id,
                challenge=challenge,
                agent_ids=competition.agent_ids,
                timeout_per_agent=timeout_per_agent
            )

            # Step 6: Determine winner (already done by AgentManager)
            winner = results.winner

            logger.info(f"Competition {competition_id} completed. Winner: {winner}")

            # Step 7-8: Update competition with winner and set status to "completed"
            await self._finalize_competition(
                competition_id=competition_id,
                winner=winner,
                results=results
            )

            logger.info(
                f"Competition {competition_id} finalized. "
                f"Duration: {results.total_duration:.2f}s"
            )

            return results

        except AgentExecutionError as e:
            logger.error(f"Agent execution error in competition {competition_id}: {e}")
            await self._update_competition_status(
                competition_id,
                CompetitionStatus.FAILED,
                error_message=str(e)
            )
            raise CompetitionServiceError(f"Competition execution failed: {e}") from e

        except Exception as e:
            logger.error(
                f"Unexpected error in competition {competition_id}: {e}",
                exc_info=True
            )
            await self._update_competition_status(
                competition_id,
                CompetitionStatus.FAILED,
                error_message=str(e)
            )
            raise CompetitionServiceError(f"Competition failed: {e}") from e

    async def get_competition_status(
        self,
        competition_id: UUID
    ) -> Optional[CompetitionResponse]:
        """
        Get the current status of a competition.

        Args:
            competition_id: UUID of the competition

        Returns:
            CompetitionResponse or None if not found
        """
        return await self._fetch_competition(competition_id)

    async def get_competition_results(
        self,
        competition_id: UUID
    ) -> Optional[CompetitionResults]:
        """
        Get the results of a completed competition.

        Args:
            competition_id: UUID of the competition

        Returns:
            CompetitionResults or None if not completed
        """
        # Fetch from database if available
        if self.database:
            return await self._fetch_competition_results(competition_id)

        # Otherwise use AgentManager's cached results
        return await self.agent_manager.get_competition_status(competition_id)

    async def cancel_competition(self, competition_id: UUID) -> bool:
        """
        Cancel a running competition.

        Args:
            competition_id: UUID of the competition to cancel

        Returns:
            True if cancelled successfully
        """
        logger.info(f"Cancelling competition {competition_id}")

        competition = await self._fetch_competition(competition_id)

        if competition.status != CompetitionStatus.RUNNING:
            logger.warning(
                f"Cannot cancel competition {competition_id} with status {competition.status.value}"
            )
            return False

        # Cancel in AgentManager
        await self.agent_manager.cancel_competition(competition_id)

        # Update database
        await self._update_competition_status(
            competition_id,
            CompetitionStatus.CANCELLED
        )

        logger.info(f"Competition {competition_id} cancelled")
        return True

    async def create_competition(
        self,
        challenge_id: str,
        agent_ids: List[UUID],
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> CompetitionResponse:
        """
        Create a new competition.

        Args:
            challenge_id: ID of the challenge
            agent_ids: List of agent UUIDs to participate
            name: Optional competition name
            description: Optional competition description

        Returns:
            CompetitionResponse with the created competition
        """
        competition = CompetitionResponse(
            id=UUID(),
            challenge_id=challenge_id,
            agent_ids=agent_ids,
            status=CompetitionStatus.PENDING,
            created_at=datetime.utcnow()
        )

        # Save to database if available
        if self.database:
            await self._save_competition(competition)

        logger.info(
            f"Created competition {competition.id} with {len(agent_ids)} agents"
        )

        return competition

    # ============================================================================
    # Private Database Methods (Stubs - will be implemented in Step 5)
    # ============================================================================

    async def _fetch_competition(self, competition_id: UUID) -> CompetitionResponse:
        """
        Fetch competition details from database.

        Args:
            competition_id: UUID of the competition

        Returns:
            CompetitionResponse

        Raises:
            CompetitionServiceError: If competition not found
        """
        if self.database:
            # TODO: Implement database query
            # query = "SELECT * FROM competitions WHERE id = $1"
            # row = await self.database.fetchrow(query, competition_id)
            # if not row:
            #     raise CompetitionServiceError(f"Competition {competition_id} not found")
            # return CompetitionResponse.from_db_row(row)
            pass

        # For now, return a mock competition
        logger.warning("Database not configured, returning mock competition")
        return CompetitionResponse(
            id=competition_id,
            challenge_id="challenge-001",
            agent_ids=[],
            status=CompetitionStatus.PENDING,
            created_at=datetime.utcnow()
        )

    async def _fetch_challenge(self, challenge_id: str) -> ChallengeResponse:
        """
        Fetch challenge details from database.

        Args:
            challenge_id: ID of the challenge

        Returns:
            ChallengeResponse

        Raises:
            CompetitionServiceError: If challenge not found
        """
        if self.database:
            # TODO: Implement database query
            # query = "SELECT * FROM challenges WHERE id = $1"
            # row = await self.database.fetchrow(query, challenge_id)
            # if not row:
            #     raise CompetitionServiceError(f"Challenge {challenge_id} not found")
            # return ChallengeResponse.from_db_row(row)
            pass

        # For now, return a mock challenge
        logger.warning("Database not configured, returning mock challenge")
        from models import TestCase, DifficultyLevel
        return ChallengeResponse(
            id=challenge_id,
            title="Mock Challenge",
            description="Mock challenge for testing",
            difficulty=DifficultyLevel.EASY,
            test_cases=[
                TestCase(input="test", expected_output="test", is_hidden=False)
            ],
            tags=[]
        )

    async def _update_competition_status(
        self,
        competition_id: UUID,
        status: CompetitionStatus,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update competition status in database.

        Args:
            competition_id: UUID of the competition
            status: New status
            started_at: Optional start time
            completed_at: Optional completion time
            error_message: Optional error message
        """
        if self.database:
            # TODO: Implement database update
            # query = """
            #     UPDATE competitions
            #     SET status = $1,
            #         started_at = COALESCE($2, started_at),
            #         completed_at = COALESCE($3, completed_at),
            #         error_message = COALESCE($4, error_message)
            #     WHERE id = $5
            # """
            # await self.database.execute(
            #     query, status.value, started_at, completed_at, error_message, competition_id
            # )
            pass

        logger.info(f"Competition {competition_id} status updated to {status.value}")

    async def _finalize_competition(
        self,
        competition_id: UUID,
        winner: Optional[UUID],
        results: CompetitionResults
    ) -> None:
        """
        Finalize competition by updating winner and status.

        Args:
            competition_id: UUID of the competition
            winner: UUID of the winning agent (or None)
            results: Complete competition results
        """
        await self._update_competition_status(
            competition_id=competition_id,
            status=CompetitionStatus.COMPLETED,
            completed_at=datetime.utcnow()
        )

        if self.database:
            # TODO: Update winner in database
            # query = "UPDATE competitions SET winner_agent_id = $1 WHERE id = $2"
            # await self.database.execute(query, winner, competition_id)

            # TODO: Update leaderboard table if needed
            # for entry in results.leaderboard:
            #     await self._save_leaderboard_entry(competition_id, entry)
            pass

        logger.info(f"Competition {competition_id} finalized with winner {winner}")

    async def _save_competition(self, competition: CompetitionResponse) -> None:
        """
        Save a new competition to database.

        Args:
            competition: Competition to save
        """
        if self.database:
            # TODO: Implement database insert
            # query = """
            #     INSERT INTO competitions (id, challenge_id, status, created_at)
            #     VALUES ($1, $2, $3, $4)
            # """
            # await self.database.execute(
            #     query,
            #     competition.id,
            #     competition.challenge_id,
            #     competition.status.value,
            #     competition.created_at
            # )
            #
            # # Insert agent relationships
            # for agent_id in competition.agent_ids:
            #     query = """
            #         INSERT INTO competition_agents (competition_id, agent_id)
            #         VALUES ($1, $2)
            #     """
            #     await self.database.execute(query, competition.id, agent_id)
            pass

        logger.info(f"Competition {competition.id} saved to database")

    async def _fetch_competition_results(
        self,
        competition_id: UUID
    ) -> Optional[CompetitionResults]:
        """
        Fetch competition results from database.

        Args:
            competition_id: UUID of the competition

        Returns:
            CompetitionResults or None if not found
        """
        if self.database:
            # TODO: Implement database query
            # Fetch competition, submissions, and build results
            pass

        return None

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def get_statistics(self) -> dict:
        """
        Get service statistics.

        Returns:
            Dictionary with service stats
        """
        stats = {
            "database_configured": self.database is not None,
            "agent_manager_stats": {
                "active_competitions": self.agent_manager.get_active_competition_count(),
                "cached_agents": len(self.agent_manager.agent_cache)
            }
        }
        return stats


# ============================================================================
# Convenience Functions
# ============================================================================

def create_competition_service(database=None) -> CompetitionService:
    """
    Create a competition service instance.

    Args:
        database: Optional database connection

    Returns:
        CompetitionService instance
    """
    return CompetitionService(database=database)
