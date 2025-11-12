"""
Agent Manager/Orchestrator for DevFork Arena.

This module is responsible for:
- Loading agents from database
- Competition orchestration (running multiple agents concurrently)
- Submission management
- Result tracking
- Timeout handling
- Resource management
"""
import asyncio
import logging
import traceback
from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import UUID
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    AgentRecord,
    AgentConfig,
    ChallengeResponse,
    SubmissionResponse,
    SubmissionStatus,
    CompetitionResponse,
    CompetitionStatus,
    CompetitionResults,
    TestResult
)
from agents.agent_factory import AgentFactory
from agents.base_agent import BaseAgent
from agents.code_executor import CodeExecutor

logger = logging.getLogger(__name__)


class AgentExecutionError(Exception):
    """Exception raised when agent execution fails"""
    pass


class AgentManager:
    """
    Manages AI agents, orchestrates competitions, and handles submissions.

    The AgentManager is responsible for:
    - Loading agent configurations from the database
    - Creating agent instances
    - Running competitions between multiple agents
    - Managing timeouts and resource cleanup
    - Tracking submissions and results
    """

    def __init__(self, database=None):
        """
        Initialize the agent manager.

        Args:
            database: Database instance for persistence (optional)
        """
        self.database = database
        self.code_executor = CodeExecutor(timeout=10)
        self.active_competitions: Dict[UUID, CompetitionResponse] = {}
        self.agent_cache: Dict[UUID, BaseAgent] = {}

        logger.info("AgentManager initialized")

    async def load_agent_from_db(self, agent_id: UUID) -> BaseAgent:
        """
        Load an agent from the database and create an instance.

        Args:
            agent_id: UUID of the agent to load

        Returns:
            BaseAgent: Instantiated agent

        Raises:
            ValueError: If agent not found or configuration invalid
            AgentExecutionError: If agent instantiation fails
        """
        logger.info(f"Loading agent {agent_id} from database")

        # Check cache first
        if agent_id in self.agent_cache:
            logger.debug(f"Agent {agent_id} found in cache")
            return self.agent_cache[agent_id]

        # Load from database
        if self.database is None:
            raise ValueError("Database not configured")

        try:
            # Fetch agent record from database
            agent_record = await self._fetch_agent_record(agent_id)

            if not agent_record:
                raise ValueError(f"Agent {agent_id} not found in database")

            if not agent_record.is_active:
                raise ValueError(f"Agent {agent_id} is inactive")

            # Create agent configuration
            config = AgentConfig(
                name=agent_record.name,
                model_provider=agent_record.model_provider,
                model_name=agent_record.model_name,
                temperature=agent_record.temperature,
                max_tokens=agent_record.max_tokens,
                max_iterations=agent_record.max_iterations,
                system_prompt=agent_record.system_prompt
            )

            # Create agent instance using factory
            agent = AgentFactory.create_agent(
                provider=agent_record.model_provider,
                config=config
            )

            # Cache the agent
            self.agent_cache[agent_id] = agent

            logger.info(f"Successfully loaded agent {agent_id}: {agent_record.name}")
            return agent

        except Exception as e:
            logger.error(f"Failed to load agent {agent_id}: {str(e)}")
            raise AgentExecutionError(f"Failed to load agent: {str(e)}")

    async def execute_agent(
        self,
        agent_id: UUID,
        challenge_id: str,
        competition_id: UUID,
        challenge: ChallengeResponse,
        timeout_seconds: int = 300
    ) -> SubmissionResponse:
        """
        Execute a single agent on a challenge.

        Args:
            agent_id: UUID of the agent
            challenge_id: Challenge identifier
            competition_id: Competition identifier
            challenge: Challenge details
            timeout_seconds: Maximum execution time in seconds

        Returns:
            SubmissionResponse: Submission result

        Raises:
            AgentExecutionError: If execution fails
        """
        logger.info(f"Executing agent {agent_id} on challenge {challenge_id}")

        submission = SubmissionResponse(
            competition_id=competition_id,
            agent_id=agent_id,
            challenge_id=challenge_id,
            code="",
            status=SubmissionStatus.PENDING,
            total_tests=len(challenge.test_cases)
        )

        try:
            # Update status to running
            submission.status = SubmissionStatus.RUNNING
            if self.database:
                await self._save_submission(submission)

            # Load agent
            agent = await self.load_agent_from_db(agent_id)

            # Execute with timeout
            start_time = time.time()

            try:
                # Run agent with timeout
                solution_code = await asyncio.wait_for(
                    agent.solve_challenge(challenge),
                    timeout=timeout_seconds
                )

                execution_time = time.time() - start_time

                # Test the solution
                test_result = self.code_executor.run_test_cases(
                    code=solution_code,
                    test_cases=challenge.test_cases
                )

                # Update submission with results
                submission.code = solution_code
                submission.execution_time = execution_time
                submission.tests_passed = test_result.passed_tests
                submission.total_tests = test_result.total_tests
                submission.attempts = len(agent.solution_attempts)

                # Determine status and score
                if test_result.passed:
                    submission.status = SubmissionStatus.PASSED
                    submission.score = self._calculate_score(
                        test_result=test_result,
                        execution_time=execution_time,
                        attempts=submission.attempts,
                        difficulty=challenge.difficulty
                    )
                else:
                    submission.status = SubmissionStatus.FAILED
                    submission.error_message = test_result.error_message or "Tests failed"
                    submission.score = 0

                logger.info(
                    f"Agent {agent_id} completed: {submission.status.value}, "
                    f"Score: {submission.score}, "
                    f"Tests: {submission.tests_passed}/{submission.total_tests}"
                )

            except asyncio.TimeoutError:
                execution_time = time.time() - start_time
                submission.status = SubmissionStatus.TIMEOUT
                submission.error_message = f"Execution timed out after {timeout_seconds} seconds"
                submission.execution_time = execution_time
                submission.score = 0
                logger.warning(f"Agent {agent_id} timed out after {timeout_seconds}s")

        except Exception as e:
            logger.error(f"Agent {agent_id} execution error: {str(e)}\n{traceback.format_exc()}")
            submission.status = SubmissionStatus.ERROR
            submission.error_message = f"Execution error: {str(e)}"
            submission.score = 0

        finally:
            # Save final submission
            if self.database:
                await self._save_submission(submission)

        return submission

    async def run_competition(
        self,
        competition_id: UUID,
        challenge: ChallengeResponse,
        agent_ids: List[UUID],
        timeout_per_agent: int = 300
    ) -> CompetitionResults:
        """
        Run a competition between multiple agents on the same challenge.

        This method orchestrates concurrent execution of multiple agents,
        manages timeouts, tracks results, and determines the winner.

        Args:
            competition_id: UUID of the competition
            challenge: Challenge to solve
            agent_ids: List of agent UUIDs to compete
            timeout_per_agent: Timeout in seconds per agent

        Returns:
            CompetitionResults: Complete competition results with rankings

        Raises:
            ValueError: If invalid competition parameters
            AgentExecutionError: If competition execution fails
        """
        logger.info(
            f"Starting competition {competition_id} with {len(agent_ids)} agents "
            f"on challenge {challenge.id}"
        )

        if not agent_ids:
            raise ValueError("No agents provided for competition")

        start_time = datetime.utcnow()

        # Create competition record
        competition = CompetitionResponse(
            id=competition_id,
            challenge_id=challenge.id,
            agent_ids=agent_ids,
            status=CompetitionStatus.RUNNING,
            started_at=start_time,
            timeout_seconds=timeout_per_agent
        )

        # Track active competition
        self.active_competitions[competition_id] = competition

        try:
            # Save competition to database
            if self.database:
                await self._save_competition(competition)

            # Execute all agents concurrently
            logger.info(f"Executing {len(agent_ids)} agents concurrently")

            tasks = [
                self.execute_agent(
                    agent_id=agent_id,
                    challenge_id=challenge.id,
                    competition_id=competition_id,
                    challenge=challenge,
                    timeout_seconds=timeout_per_agent
                )
                for agent_id in agent_ids
            ]

            # Wait for all agents to complete
            submissions = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and convert to submissions
            valid_submissions = []
            for i, result in enumerate(submissions):
                if isinstance(result, Exception):
                    logger.error(f"Agent {agent_ids[i]} failed with exception: {result}")
                    # Create error submission
                    error_submission = SubmissionResponse(
                        competition_id=competition_id,
                        agent_id=agent_ids[i],
                        challenge_id=challenge.id,
                        code="",
                        status=SubmissionStatus.ERROR,
                        error_message=str(result),
                        total_tests=len(challenge.test_cases)
                    )
                    valid_submissions.append(error_submission)
                else:
                    valid_submissions.append(result)

            # Calculate rankings and determine winner
            leaderboard = self._create_leaderboard(valid_submissions)
            winner = leaderboard[0]["agent_id"] if leaderboard else None

            # Complete competition
            end_time = datetime.utcnow()
            competition.status = CompetitionStatus.COMPLETED
            competition.completed_at = end_time

            if self.database:
                await self._save_competition(competition)

            # Create results
            results = CompetitionResults(
                competition_id=competition_id,
                challenge=challenge,
                submissions=valid_submissions,
                winner=winner,
                leaderboard=leaderboard,
                started_at=start_time,
                completed_at=end_time,
                total_duration=(end_time - start_time).total_seconds()
            )

            logger.info(
                f"Competition {competition_id} completed. "
                f"Winner: {winner}, Duration: {results.total_duration:.2f}s"
            )

            return results

        except Exception as e:
            logger.error(f"Competition {competition_id} failed: {str(e)}\n{traceback.format_exc()}")
            competition.status = CompetitionStatus.CANCELLED
            if self.database:
                await self._save_competition(competition)
            raise AgentExecutionError(f"Competition failed: {str(e)}")

        finally:
            # Remove from active competitions
            self.active_competitions.pop(competition_id, None)
            # Clean up resources
            await self.cleanup()

    def _calculate_score(
        self,
        test_result: TestResult,
        execution_time: float,
        attempts: int,
        difficulty: str
    ) -> int:
        """
        Calculate score based on test results, execution time, and attempts.

        Scoring formula:
        - Base score: 100 points for passing all tests
        - Time bonus: Faster execution gets bonus points
        - Attempt penalty: More attempts reduce score
        - Difficulty multiplier: Harder challenges give more points

        Args:
            test_result: Test execution results
            execution_time: Time taken in seconds
            attempts: Number of attempts made
            difficulty: Challenge difficulty level

        Returns:
            int: Calculated score
        """
        if not test_result.passed:
            # Partial credit for partially passing tests
            return int((test_result.passed_tests / test_result.total_tests) * 30)

        # Base score for passing all tests
        base_score = 100

        # Difficulty multiplier
        difficulty_multiplier = {
            "easy": 1.0,
            "medium": 1.5,
            "hard": 2.0
        }.get(difficulty.lower(), 1.0)

        # Time bonus (faster is better, max 50 bonus points)
        # Assuming 60 seconds is baseline
        time_bonus = max(0, 50 - (execution_time / 60 * 50))

        # Attempt penalty (first attempt gets no penalty, subsequent attempts lose points)
        attempt_penalty = (attempts - 1) * 10

        # Calculate final score
        score = int((base_score + time_bonus - attempt_penalty) * difficulty_multiplier)

        return max(0, score)  # Ensure non-negative

    def _create_leaderboard(self, submissions: List[SubmissionResponse]) -> List[Dict[str, Any]]:
        """
        Create a ranked leaderboard from submissions.

        Args:
            submissions: List of all submissions

        Returns:
            List of leaderboard entries, sorted by rank
        """
        leaderboard = []

        for submission in submissions:
            entry = {
                "rank": 0,  # Will be set after sorting
                "agent_id": submission.agent_id,
                "score": submission.score,
                "status": submission.status.value,
                "tests_passed": submission.tests_passed,
                "total_tests": submission.total_tests,
                "execution_time": submission.execution_time,
                "attempts": submission.attempts
            }
            leaderboard.append(entry)

        # Sort by score (descending), then by execution time (ascending)
        leaderboard.sort(
            key=lambda x: (-x["score"], x["execution_time"] or float('inf'))
        )

        # Assign ranks
        for i, entry in enumerate(leaderboard, 1):
            entry["rank"] = i

        return leaderboard

    async def _fetch_agent_record(self, agent_id: UUID) -> Optional[AgentRecord]:
        """
        Fetch agent record from database.

        This is a placeholder that should be implemented with actual
        database queries when database is configured.

        Args:
            agent_id: Agent UUID

        Returns:
            AgentRecord or None
        """
        if self.database is None:
            # For testing without database, return a mock record
            logger.warning("Database not configured, using mock agent record")
            return AgentRecord(
                id=agent_id,
                name="Mock Agent",
                model_provider="openai",
                model_name="gpt-4-turbo-preview",
                temperature=0.7,
                max_tokens=4096,
                max_iterations=3
            )

        # TODO: Implement actual database query
        # Example:
        # query = "SELECT * FROM agents WHERE id = $1"
        # result = await self.database.execute_query(query, (str(agent_id),))
        # return AgentRecord(**result[0]) if result else None

        return None

    async def _save_submission(self, submission: SubmissionResponse) -> None:
        """
        Save submission to database.

        Args:
            submission: Submission to save
        """
        if self.database is None:
            logger.debug("Database not configured, skipping submission save")
            return

        # TODO: Implement actual database insert/update
        # Example:
        # query = """
        # INSERT INTO submissions (id, competition_id, agent_id, ...)
        # VALUES ($1, $2, $3, ...)
        # ON CONFLICT (id) DO UPDATE SET ...
        # """
        # await self.database.execute_query(query, submission.dict().values())

        logger.debug(f"Saved submission {submission.id} to database")

    async def _save_competition(self, competition: CompetitionResponse) -> None:
        """
        Save competition to database.

        Args:
            competition: Competition to save
        """
        if self.database is None:
            logger.debug("Database not configured, skipping competition save")
            return

        # TODO: Implement actual database insert/update
        logger.debug(f"Saved competition {competition.id} to database")

    async def get_competition_status(self, competition_id: UUID) -> Optional[CompetitionResponse]:
        """
        Get current status of a competition.

        Args:
            competition_id: Competition UUID

        Returns:
            CompetitionResponse or None if not found
        """
        # Check active competitions first
        if competition_id in self.active_competitions:
            return self.active_competitions[competition_id]

        # Check database
        if self.database:
            # TODO: Implement database query
            pass

        return None

    async def cancel_competition(self, competition_id: UUID) -> bool:
        """
        Cancel a running competition.

        Args:
            competition_id: Competition UUID

        Returns:
            bool: True if cancelled successfully
        """
        if competition_id not in self.active_competitions:
            logger.warning(f"Competition {competition_id} not found or not running")
            return False

        competition = self.active_competitions[competition_id]
        competition.status = CompetitionStatus.CANCELLED

        if self.database:
            await self._save_competition(competition)

        self.active_competitions.pop(competition_id, None)

        logger.info(f"Cancelled competition {competition_id}")
        return True

    async def cleanup(self) -> None:
        """
        Clean up resources and cached agents.

        This method should be called periodically to free up memory.
        """
        # Clear old cached agents
        logger.debug("Cleaning up agent cache")
        self.agent_cache.clear()

        # Any other cleanup tasks
        logger.debug("Cleanup completed")

    def get_active_competition_count(self) -> int:
        """
        Get the number of currently running competitions.

        Returns:
            int: Number of active competitions
        """
        return len(self.active_competitions)
