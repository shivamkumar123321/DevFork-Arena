"""
Competition Demo - Showcases the AgentManager and competition orchestration.

This script demonstrates:
- Creating multiple agents
- Running a competition between agents
- Viewing results and leaderboards
- Managing competitions
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
from agents import AgentManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_challenge() -> ChallengeResponse:
    """Create a sample challenge for the competition."""
    return ChallengeResponse(
        id="challenge-001",
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
            name="GPT-4 Turbo Competitor",
            model_provider="openai",
            model_name="gpt-4-turbo-preview",
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
        AgentRecord(
            id=uuid4(),
            name="Claude Sonnet Thinker",
            model_provider="anthropic",
            model_name="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=4096,
            max_iterations=3
        ),
    ]


async def demo_basic_competition():
    """
    Demonstrate a basic competition between multiple agents.
    """
    logger.info("\n" + "="*60)
    logger.info("BASIC COMPETITION DEMO")
    logger.info("="*60 + "\n")

    # Create agent manager
    manager = AgentManager()

    # Create sample data
    challenge = create_sample_challenge()
    agents = create_sample_agents()

    logger.info(f"Challenge: {challenge.title}")
    logger.info(f"Difficulty: {challenge.difficulty.value}")
    logger.info(f"Number of agents: {len(agents)}\n")

    for agent in agents:
        logger.info(f"  - {agent.name} ({agent.model_provider}/{agent.model_name})")

    logger.info("\n" + "-"*60)
    logger.info("Starting competition...")
    logger.info("-"*60 + "\n")

    # Run competition
    competition_id = uuid4()
    agent_ids = [agent.id for agent in agents]

    try:
        results = await manager.run_competition(
            competition_id=competition_id,
            challenge=challenge,
            agent_ids=agent_ids,
            timeout_per_agent=180  # 3 minutes per agent
        )

        # Display results
        logger.info("\n" + "="*60)
        logger.info("COMPETITION RESULTS")
        logger.info("="*60 + "\n")

        logger.info(f"Competition ID: {results.competition_id}")
        logger.info(f"Total Duration: {results.total_duration:.2f}s")
        logger.info(f"Winner: {results.winner}\n")

        logger.info("LEADERBOARD:")
        logger.info("-"*60)
        for entry in results.leaderboard:
            logger.info(
                f"#{entry['rank']}: Agent {entry['agent_id']} - "
                f"Score: {entry['score']}, "
                f"Status: {entry['status']}, "
                f"Tests: {entry['tests_passed']}/{entry['total_tests']}, "
                f"Time: {entry['execution_time']:.2f}s"
            )

        logger.info("\n" + "-"*60)
        logger.info("DETAILED SUBMISSIONS:")
        logger.info("-"*60 + "\n")

        for submission in results.submissions:
            logger.info(f"Agent: {submission.agent_id}")
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


async def demo_single_agent_execution():
    """
    Demonstrate executing a single agent on a challenge.
    """
    logger.info("\n" + "="*60)
    logger.info("SINGLE AGENT EXECUTION DEMO")
    logger.info("="*60 + "\n")

    # Create agent manager
    manager = AgentManager()

    # Create sample data
    challenge = create_sample_challenge()
    agent = create_sample_agents()[0]  # Use first agent

    logger.info(f"Challenge: {challenge.title}")
    logger.info(f"Agent: {agent.name} ({agent.model_provider}/{agent.model_name})\n")

    logger.info("Executing agent...")

    # Execute single agent
    competition_id = uuid4()

    try:
        submission = await manager.execute_agent(
            agent_id=agent.id,
            challenge_id=challenge.id,
            competition_id=competition_id,
            challenge=challenge,
            timeout_seconds=180
        )

        logger.info("\n" + "-"*60)
        logger.info("EXECUTION RESULT:")
        logger.info("-"*60)
        logger.info(f"Status: {submission.status.value}")
        logger.info(f"Score: {submission.score}")
        logger.info(f"Tests Passed: {submission.tests_passed}/{submission.total_tests}")
        logger.info(f"Execution Time: {submission.execution_time:.2f}s" if submission.execution_time else "N/A")
        logger.info(f"Attempts: {submission.attempts}")

        if submission.status.value == "passed":
            logger.info("\nGenerated Solution:")
            logger.info("-"*60)
            logger.info(submission.code)

        if submission.error_message:
            logger.info(f"\nError: {submission.error_message}")

    except Exception as e:
        logger.error(f"Execution failed: {str(e)}", exc_info=True)


async def demo_competition_with_timeout():
    """
    Demonstrate competition with timeout handling.
    """
    logger.info("\n" + "="*60)
    logger.info("COMPETITION WITH TIMEOUT DEMO")
    logger.info("="*60 + "\n")

    # Create agent manager
    manager = AgentManager()

    # Create sample data
    challenge = create_sample_challenge()
    agents = create_sample_agents()[:2]  # Use first 2 agents

    logger.info(f"Challenge: {challenge.title}")
    logger.info(f"Timeout per agent: 5 seconds (very short for demo)\n")

    # Run competition with very short timeout
    competition_id = uuid4()
    agent_ids = [agent.id for agent in agents]

    try:
        results = await manager.run_competition(
            competition_id=competition_id,
            challenge=challenge,
            agent_ids=agent_ids,
            timeout_per_agent=5  # Very short timeout to trigger timeout handling
        )

        logger.info("\nResults:")
        for entry in results.leaderboard:
            logger.info(
                f"Agent {entry['agent_id']}: "
                f"Status={entry['status']}, "
                f"Score={entry['score']}"
            )

    except Exception as e:
        logger.error(f"Competition failed: {str(e)}", exc_info=True)


async def demo_manager_stats():
    """
    Demonstrate agent manager statistics and monitoring.
    """
    logger.info("\n" + "="*60)
    logger.info("MANAGER STATISTICS DEMO")
    logger.info("="*60 + "\n")

    manager = AgentManager()

    logger.info(f"Active competitions: {manager.get_active_competition_count()}")
    logger.info(f"Cached agents: {len(manager.agent_cache)}")

    # Create a competition
    challenge = create_sample_challenge()
    agents = create_sample_agents()[:2]
    competition_id = uuid4()

    # Start competition in background
    logger.info("\nStarting competition in background...")

    task = asyncio.create_task(
        manager.run_competition(
            competition_id=competition_id,
            challenge=challenge,
            agent_ids=[a.id for a in agents],
            timeout_per_agent=180
        )
    )

    # Give it a moment to start
    await asyncio.sleep(1)

    logger.info(f"Active competitions: {manager.get_active_competition_count()}")

    # Get competition status
    status = await manager.get_competition_status(competition_id)
    if status:
        logger.info(f"Competition status: {status.status.value}")

    # Wait for completion
    await task

    logger.info(f"Active competitions after completion: {manager.get_active_competition_count()}")


async def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("DevFork Arena - Competition & Agent Manager Demo")
    print("="*60 + "\n")

    print("This demo showcases the AgentManager and competition system.")
    print("Choose a demo to run:\n")
    print("1. Basic Competition (Multiple Agents)")
    print("2. Single Agent Execution")
    print("3. Competition with Timeout Handling")
    print("4. Manager Statistics & Monitoring")
    print("5. Run All Demos")
    print("0. Exit\n")

    choice = input("Enter your choice (0-5): ").strip()

    if choice == "1":
        await demo_basic_competition()
    elif choice == "2":
        await demo_single_agent_execution()
    elif choice == "3":
        await demo_competition_with_timeout()
    elif choice == "4":
        await demo_manager_stats()
    elif choice == "5":
        await demo_single_agent_execution()
        await demo_basic_competition()
        await demo_competition_with_timeout()
        await demo_manager_stats()
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
