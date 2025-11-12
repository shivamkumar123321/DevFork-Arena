"""
Competition Service Demo

Demonstrates the high-level CompetitionService that orchestrates
the entire competition lifecycle with status management and database
integration.
"""
import asyncio
import sys
import os
import logging
from uuid import uuid4

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    ChallengeResponse,
    TestCase,
    DifficultyLevel,
    AgentRecord
)
from services import CompetitionService, create_competition_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_challenge() -> ChallengeResponse:
    """Create a sample challenge for the competition."""
    return ChallengeResponse(
        id="challenge-two-sum",
        title="Two Sum",
        description="""Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.""",
        difficulty=DifficultyLevel.EASY,
        test_cases=[
            TestCase(input="[2,7,11,15], 9", expected_output="[0,1]", is_hidden=False),
            TestCase(input="[3,2,4], 6", expected_output="[1,2]", is_hidden=False),
            TestCase(input="[3,3], 6", expected_output="[0,1]", is_hidden=False),
        ],
        constraints="2 <= nums.length <= 10^4, -10^9 <= nums[i] <= 10^9",
        time_limit=60,
        memory_limit=256,
        tags=["array", "hash-table"]
    )


def create_sample_agents() -> list[AgentRecord]:
    """Create sample agent records for the competition."""
    return [
        AgentRecord(
            id=uuid4(),
            name="GPT-4 Turbo Pro",
            model_provider="openai",
            model_name="gpt-4-turbo-preview",
            temperature=0.7,
            max_tokens=4096,
            max_iterations=3
        ),
        AgentRecord(
            id=uuid4(),
            name="Claude Sonnet Elite",
            model_provider="anthropic",
            model_name="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=4096,
            max_iterations=3
        ),
        AgentRecord(
            id=uuid4(),
            name="GPT-3.5 Speedster",
            model_provider="openai",
            model_name="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=2048,
            max_iterations=2
        ),
    ]


async def demo_full_competition_flow():
    """
    Demonstrate the complete competition flow using CompetitionService.

    This shows the high-level orchestration:
    1. Create competition
    2. Run competition (handles all status updates internally)
    3. View results
    """
    logger.info("\n" + "="*60)
    logger.info("FULL COMPETITION FLOW DEMO")
    logger.info("="*60 + "\n")

    # Create service (without database for now)
    service = create_competition_service(database=None)

    # Create sample data
    challenge = create_sample_challenge()
    agents = create_sample_agents()
    agent_ids = [agent.id for agent in agents]

    logger.info(f"Challenge: {challenge.title}")
    logger.info(f"Difficulty: {challenge.difficulty.value}")
    logger.info(f"Number of agents: {len(agents)}\n")

    for agent in agents:
        logger.info(f"  - {agent.name} ({agent.model_provider}/{agent.model_name})")

    # Step 1: Create competition
    logger.info("\n" + "-"*60)
    logger.info("Step 1: Creating competition...")
    logger.info("-"*60 + "\n")

    competition = await service.create_competition(
        challenge_id=challenge.id,
        agent_ids=agent_ids,
        name="Two Sum Challenge",
        description="Test competition for Two Sum problem"
    )

    logger.info(f"Competition created: {competition.id}")
    logger.info(f"Initial status: {competition.status.value}")

    # Step 2: Run competition (handles all orchestration internally)
    logger.info("\n" + "-"*60)
    logger.info("Step 2: Running competition...")
    logger.info("-"*60 + "\n")
    logger.info("(Service will automatically:")
    logger.info("  - Update status to 'running'")
    logger.info("  - Execute all agents concurrently")
    logger.info("  - Determine winner")
    logger.info("  - Update status to 'completed')\n")

    try:
        results = await service.run_competition(
            competition_id=competition.id,
            timeout_per_agent=180  # 3 minutes per agent
        )

        # Step 3: Display results
        logger.info("\n" + "="*60)
        logger.info("COMPETITION RESULTS")
        logger.info("="*60 + "\n")

        logger.info(f"Competition ID: {results.competition_id}")
        logger.info(f"Total Duration: {results.total_duration:.2f}s")
        logger.info(f"Winner: {results.winner}\n")

        logger.info("LEADERBOARD:")
        logger.info("-"*60)
        for entry in results.leaderboard:
            agent_name = next(
                (a.name for a in agents if a.id == entry['agent_id']),
                "Unknown"
            )
            logger.info(
                f"#{entry['rank']}: {agent_name} - "
                f"Score: {entry['score']}, "
                f"Status: {entry['status']}, "
                f"Tests: {entry['tests_passed']}/{entry['total_tests']}, "
                f"Time: {entry['execution_time']:.2f}s"
            )

        logger.info("\n" + "-"*60)
        logger.info("DETAILED SUBMISSIONS:")
        logger.info("-"*60 + "\n")

        for submission in results.submissions:
            agent_name = next(
                (a.name for a in agents if a.id == submission.agent_id),
                "Unknown"
            )
            logger.info(f"Agent: {agent_name}")
            logger.info(f"Status: {submission.status.value}")
            logger.info(f"Score: {submission.score}")
            logger.info(f"Tests Passed: {submission.tests_passed}/{submission.total_tests}")
            logger.info(f"Execution Time: {submission.execution_time:.2f}s" if submission.execution_time else "N/A")
            logger.info(f"Attempts: {submission.attempts}")
            if submission.error_message:
                logger.info(f"Error: {submission.error_message}")
            logger.info("")

    except Exception as e:
        logger.error(f"Competition failed: {str(e)}", exc_info=True)


async def demo_service_status_checking():
    """
    Demonstrate checking competition status.
    """
    logger.info("\n" + "="*60)
    logger.info("SERVICE STATUS CHECKING DEMO")
    logger.info("="*60 + "\n")

    service = create_competition_service()

    # Create and start a competition
    challenge = create_sample_challenge()
    agents = create_sample_agents()[:2]  # Use 2 agents for faster demo

    competition = await service.create_competition(
        challenge_id=challenge.id,
        agent_ids=[a.id for a in agents]
    )

    logger.info(f"Competition created: {competition.id}")

    # Check initial status
    status = await service.get_competition_status(competition.id)
    logger.info(f"Initial status: {status.status.value if status else 'Not found'}")

    # Start competition in background
    logger.info("\nStarting competition in background...")

    task = asyncio.create_task(
        service.run_competition(
            competition_id=competition.id,
            timeout_per_agent=180
        )
    )

    # Give it a moment to start
    await asyncio.sleep(1)

    # Check running status
    status = await service.get_competition_status(competition.id)
    logger.info(f"Status after start: {status.status.value if status else 'Not found'}")

    # Wait for completion
    logger.info("\nWaiting for competition to complete...")
    results = await task

    # Check final status
    status = await service.get_competition_status(competition.id)
    logger.info(f"Final status: {status.status.value if status else 'Not found'}")
    logger.info(f"Winner: {results.winner}")


async def demo_service_statistics():
    """
    Demonstrate getting service statistics.
    """
    logger.info("\n" + "="*60)
    logger.info("SERVICE STATISTICS DEMO")
    logger.info("="*60 + "\n")

    service = create_competition_service()

    # Get initial stats
    stats = service.get_statistics()
    logger.info("Service Statistics:")
    logger.info(f"  Database Configured: {stats['database_configured']}")
    logger.info(f"  Active Competitions: {stats['agent_manager_stats']['active_competitions']}")
    logger.info(f"  Cached Agents: {stats['agent_manager_stats']['cached_agents']}")

    # Create and run a competition
    challenge = create_sample_challenge()
    agents = create_sample_agents()[:2]

    competition = await service.create_competition(
        challenge_id=challenge.id,
        agent_ids=[a.id for a in agents]
    )

    # Start in background
    task = asyncio.create_task(
        service.run_competition(
            competition_id=competition.id,
            timeout_per_agent=180
        )
    )

    await asyncio.sleep(1)

    # Get stats while running
    stats = service.get_statistics()
    logger.info("\nStatistics during competition:")
    logger.info(f"  Active Competitions: {stats['agent_manager_stats']['active_competitions']}")
    logger.info(f"  Cached Agents: {stats['agent_manager_stats']['cached_agents']}")

    # Wait for completion
    await task

    # Get final stats
    stats = service.get_statistics()
    logger.info("\nStatistics after completion:")
    logger.info(f"  Active Competitions: {stats['agent_manager_stats']['active_competitions']}")
    logger.info(f"  Cached Agents: {stats['agent_manager_stats']['cached_agents']}")


async def demo_error_handling():
    """
    Demonstrate error handling in the service.
    """
    logger.info("\n" + "="*60)
    logger.info("ERROR HANDLING DEMO")
    logger.info("="*60 + "\n")

    service = create_competition_service()

    # Try to run a non-existent competition
    logger.info("Attempting to run non-existent competition...")
    fake_id = uuid4()

    try:
        await service.run_competition(
            competition_id=fake_id,
            timeout_per_agent=60
        )
    except Exception as e:
        logger.info(f"Expected error caught: {type(e).__name__}: {e}")

    # Try to run already completed competition
    logger.info("\nAttempting to run already completed competition...")
    # This would require database support, so we'll skip for now
    logger.info("(Requires database support)")


async def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("DevFork Arena - Competition Service Demo")
    print("="*60 + "\n")

    print("This demo showcases the high-level CompetitionService.")
    print("The service orchestrates the entire competition lifecycle:\n")
    print("  - Status management (pending → running → completed)")
    print("  - Agent execution coordination")
    print("  - Winner determination")
    print("  - Database integration (stub for now)\n")

    print("Choose a demo to run:\n")
    print("1. Full Competition Flow (End-to-End)")
    print("2. Status Checking")
    print("3. Service Statistics")
    print("4. Error Handling")
    print("5. Run All Demos")
    print("0. Exit\n")

    choice = input("Enter your choice (0-5): ").strip()

    if choice == "1":
        await demo_full_competition_flow()
    elif choice == "2":
        await demo_service_status_checking()
    elif choice == "3":
        await demo_service_statistics()
    elif choice == "4":
        await demo_error_handling()
    elif choice == "5":
        await demo_full_competition_flow()
        await demo_service_status_checking()
        await demo_service_statistics()
        await demo_error_handling()
    elif choice == "0":
        print("Exiting...")
        return
    else:
        print("Invalid choice!")

    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)
