"""
Demo script for testing AI agents on coding challenges.

This script demonstrates how to use the AI agent system to solve coding challenges.
It creates sample challenges and shows how different agents can solve them.
"""
import asyncio
import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import ChallengeResponse, TestCase, DifficultyLevel, AgentConfig
from agents import AgentFactory, create_claude_agent, create_openai_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_challenges():
    """Create sample coding challenges for testing."""

    # Challenge 1: Two Sum (Easy)
    two_sum = ChallengeResponse(
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
        constraints="2 <= nums.length <= 10^4, -10^9 <= nums[i] <= 10^9, -10^9 <= target <= 10^9",
        time_limit=60,
        memory_limit=256,
        tags=["array", "hash-table"]
    )

    # Challenge 2: Palindrome Number (Easy)
    palindrome = ChallengeResponse(
        id="challenge-002",
        title="Palindrome Number",
        description="""Given an integer x, return true if x is a palindrome, and false otherwise.

An integer is a palindrome when it reads the same backward as forward.

For example, 121 is a palindrome while 123 is not.""",
        difficulty=DifficultyLevel.EASY,
        test_cases=[
            TestCase(input="121", expected_output="True", is_hidden=False),
            TestCase(input="-121", expected_output="False", is_hidden=False),
            TestCase(input="10", expected_output="False", is_hidden=False),
        ],
        constraints="-2^31 <= x <= 2^31 - 1",
        time_limit=60,
        memory_limit=256,
        tags=["math"]
    )

    # Challenge 3: Reverse String (Easy)
    reverse_string = ChallengeResponse(
        id="challenge-003",
        title="Reverse String",
        description="""Write a function that reverses a string. The input string is given as an array of characters s.

You must do this by modifying the input array in-place with O(1) extra memory.

Return the reversed array as a list.""",
        difficulty=DifficultyLevel.EASY,
        test_cases=[
            TestCase(input="['h','e','l','l','o']", expected_output="['o','l','l','e','h']", is_hidden=False),
            TestCase(input="['H','a','n','n','a','h']", expected_output="['h','a','n','n','a','H']", is_hidden=False),
        ],
        constraints="1 <= s.length <= 10^5",
        time_limit=60,
        memory_limit=256,
        tags=["string", "two-pointers"]
    )

    return [two_sum, palindrome, reverse_string]


async def test_agent_with_challenge(agent, challenge):
    """
    Test an agent with a specific challenge.

    Args:
        agent: AI agent to test
        challenge: Challenge to solve

    Returns:
        Dict with results
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing {agent.config.name} on: {challenge.title}")
    logger.info(f"Difficulty: {challenge.difficulty.value}")
    logger.info(f"{'='*60}\n")

    try:
        # Solve the challenge
        solution_code = await agent.solve_challenge(challenge)

        # Get performance summary
        performance = agent.get_performance_summary()

        logger.info(f"\n{'='*60}")
        logger.info(f"RESULTS for {agent.config.name}")
        logger.info(f"{'='*60}")
        logger.info(f"Success: {performance['success']}")
        logger.info(f"Attempts: {performance['total_attempts']}")
        logger.info(f"Tests Passed: {performance['final_attempt']['tests_passed']}/{performance['final_attempt']['total_tests']}")
        logger.info(f"\nGenerated Solution:\n{'-'*60}")
        logger.info(solution_code)
        logger.info(f"{'-'*60}\n")

        return {
            "success": True,
            "performance": performance,
            "code": solution_code
        }

    except Exception as e:
        logger.error(f"Failed to solve challenge: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


async def demo_claude_agent():
    """Demonstrate Claude agent solving challenges."""
    logger.info("\n" + "="*60)
    logger.info("CLAUDE AGENT DEMONSTRATION")
    logger.info("="*60 + "\n")

    # Create Claude agent
    agent = create_claude_agent(
        model_name="claude-3-5-sonnet-20241022",
        temperature=0.7,
        max_iterations=3
    )

    logger.info(f"Created agent: {agent.get_model_info()}\n")

    # Get sample challenges
    challenges = create_sample_challenges()

    # Test on first challenge
    await test_agent_with_challenge(agent, challenges[0])


async def demo_openai_agent():
    """Demonstrate OpenAI agent solving challenges."""
    logger.info("\n" + "="*60)
    logger.info("OPENAI AGENT DEMONSTRATION")
    logger.info("="*60 + "\n")

    # Create OpenAI agent
    agent = create_openai_agent(
        model_name="gpt-4-turbo-preview",
        temperature=0.7,
        max_iterations=3
    )

    logger.info(f"Created agent: {agent.get_model_info()}\n")

    # Get sample challenges
    challenges = create_sample_challenges()

    # Test on first challenge
    await test_agent_with_challenge(agent, challenges[0])


async def demo_agent_comparison():
    """Compare multiple agents on the same challenge."""
    logger.info("\n" + "="*60)
    logger.info("AGENT COMPARISON")
    logger.info("="*60 + "\n")

    # Create different agents
    claude_agent = create_claude_agent(name="Claude Sonnet")
    openai_agent = create_openai_agent(name="GPT-4 Turbo")

    # Get a challenge
    challenges = create_sample_challenges()
    challenge = challenges[0]

    logger.info(f"Challenge: {challenge.title}\n")

    # Test both agents
    results = {}

    for agent in [claude_agent, openai_agent]:
        result = await test_agent_with_challenge(agent, challenge)
        results[agent.config.name] = result

    # Summary
    logger.info("\n" + "="*60)
    logger.info("COMPARISON SUMMARY")
    logger.info("="*60)

    for agent_name, result in results.items():
        if result["success"]:
            perf = result["performance"]
            logger.info(f"\n{agent_name}:")
            logger.info(f"  Success: ✓")
            logger.info(f"  Attempts: {perf['total_attempts']}")
            logger.info(f"  Tests: {perf['final_attempt']['tests_passed']}/{perf['final_attempt']['total_tests']}")
        else:
            logger.info(f"\n{agent_name}:")
            logger.info(f"  Success: ✗")
            logger.info(f"  Error: {result['error']}")


async def demo_agent_factory():
    """Demonstrate using the AgentFactory."""
    logger.info("\n" + "="*60)
    logger.info("AGENT FACTORY DEMONSTRATION")
    logger.info("="*60 + "\n")

    # List supported providers
    providers = AgentFactory.list_supported_providers()
    logger.info(f"Supported providers: {providers}\n")

    # Create agents using factory
    claude = AgentFactory.create_agent("claude", temperature=0.5)
    openai = AgentFactory.create_agent("openai", temperature=0.5)

    logger.info(f"Created Claude agent: {claude.get_model_info()}")
    logger.info(f"Created OpenAI agent: {openai.get_model_info()}\n")

    # Test with a simple challenge
    challenges = create_sample_challenges()
    await test_agent_with_challenge(claude, challenges[1])


async def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("DevFork Arena - AI Agent System Demo")
    print("="*60 + "\n")

    print("This demo will show how AI agents solve coding challenges.")
    print("Choose a demo to run:\n")
    print("1. Claude Agent Demo")
    print("2. OpenAI Agent Demo")
    print("3. Agent Comparison")
    print("4. Agent Factory Demo")
    print("5. Run All Demos")
    print("0. Exit\n")

    choice = input("Enter your choice (0-5): ").strip()

    if choice == "1":
        await demo_claude_agent()
    elif choice == "2":
        await demo_openai_agent()
    elif choice == "3":
        await demo_agent_comparison()
    elif choice == "4":
        await demo_agent_factory()
    elif choice == "5":
        await demo_claude_agent()
        await demo_openai_agent()
        await demo_agent_comparison()
        await demo_agent_factory()
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
