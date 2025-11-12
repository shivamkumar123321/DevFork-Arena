"""
Test Agents for Validation

Special agent implementations for testing and validation:
1. AlwaysPassAgent - Returns hardcoded correct solutions
2. AlwaysFailAgent - Returns incorrect solutions
3. TimeoutAgent - Simulates timeout scenarios
4. RandomAgent - Random success/failure for stress testing

These agents are used for testing the competition system without
relying on actual LLM API calls.
"""
import asyncio
from typing import Optional
from datetime import datetime

from models import ChallengeResponse, AgentConfig
from agents.base_agent import BaseAgent, SolutionAttempt


class AlwaysPassAgent(BaseAgent):
    """
    Test agent that always returns correct hardcoded solutions.

    Used for testing the competition flow with guaranteed success.
    Solutions are predefined for common challenges like FizzBuzz,
    Two Sum, etc.
    """

    # Hardcoded solutions for common challenges
    SOLUTIONS = {
        "fizzbuzz": '''def fizzbuzz(n):
    """Generate FizzBuzz sequence up to n."""
    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result
''',
        "two-sum": '''def two_sum(nums, target):
    """Find two numbers that add up to target."""
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
''',
        "reverse-string": '''def reverse_string(s):
    """Reverse a string."""
    return s[::-1]
''',
        "palindrome": '''def is_palindrome(s):
    """Check if string is a palindrome."""
    s = ''.join(c.lower() for c in s if c.isalnum())
    return s == s[::-1]
''',
        "factorial": '''def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)
''',
        "fibonacci": '''def fibonacci(n):
    """Return nth Fibonacci number."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
''',
    }

    def __init__(self, name: str = "AlwaysPassAgent", **kwargs):
        """Initialize AlwaysPassAgent."""
        config = AgentConfig(
            name=name,
            model_provider="test",
            model_name="always-pass",
            temperature=0.0,
            max_tokens=1000,
            max_iterations=1  # Only needs one attempt
        )
        super().__init__(config)
        self.solution_delay = kwargs.get("solution_delay", 0.1)  # Simulate thinking

    async def _generate_code(self, prompt: str) -> str:
        """Generate hardcoded solution based on challenge."""
        # Simulate thinking time
        await asyncio.sleep(self.solution_delay)

        # Detect challenge type from prompt
        prompt_lower = prompt.lower()

        for challenge_key, solution in self.SOLUTIONS.items():
            if challenge_key in prompt_lower:
                return solution

        # Default solution for unknown challenges
        return '''def solution(*args, **kwargs):
    """Generic solution that tries to pass."""
    if args:
        return args[0]
    return "solution"
'''

    async def analyze_and_iterate(
        self,
        challenge: ChallengeResponse,
        previous_code: str,
        error_message: str
    ) -> str:
        """
        Not needed for AlwaysPassAgent since it passes on first try.
        """
        return previous_code


class AlwaysFailAgent(BaseAgent):
    """
    Test agent that always returns incorrect solutions.

    Used for testing error handling and competition ranking
    when agents fail.
    """

    def __init__(self, name: str = "AlwaysFailAgent", **kwargs):
        """Initialize AlwaysFailAgent."""
        config = AgentConfig(
            name=name,
            model_provider="test",
            model_name="always-fail",
            temperature=0.0,
            max_tokens=1000,
            max_iterations=3  # Will try 3 times and fail
        )
        super().__init__(config)
        self.solution_delay = kwargs.get("solution_delay", 0.1)

    async def _generate_code(self, prompt: str) -> str:
        """Generate intentionally incorrect solution."""
        await asyncio.sleep(self.solution_delay)

        # Return code that is syntactically valid but logically wrong
        return '''def solution(*args, **kwargs):
    """Intentionally incorrect solution."""
    return "WRONG ANSWER"
'''

    async def analyze_and_iterate(
        self,
        challenge: ChallengeResponse,
        previous_code: str,
        error_message: str
    ) -> str:
        """
        Generate different wrong solutions on each iteration.
        """
        await asyncio.sleep(self.solution_delay)

        # Return increasingly complex but still wrong solutions
        attempts = len(self.solution_attempts)

        if attempts == 1:
            return '''def solution(*args, **kwargs):
    """Second attempt - still wrong."""
    return None
'''
        else:
            return '''def solution(*args, **kwargs):
    """Third attempt - still wrong."""
    return []
'''


class TimeoutAgent(BaseAgent):
    """
    Test agent that simulates timeout scenarios.

    Used for testing timeout handling in competitions.
    """

    def __init__(self, name: str = "TimeoutAgent", timeout_duration: int = 10, **kwargs):
        """
        Initialize TimeoutAgent.

        Args:
            name: Agent name
            timeout_duration: How long to sleep before returning (seconds)
        """
        config = AgentConfig(
            name=name,
            model_provider="test",
            model_name="timeout",
            temperature=0.0,
            max_tokens=1000,
            max_iterations=1
        )
        super().__init__(config)
        self.timeout_duration = timeout_duration

    async def _generate_code(self, prompt: str) -> str:
        """Sleep for timeout_duration before returning solution."""
        # This will cause timeout if timeout_duration > configured timeout
        await asyncio.sleep(self.timeout_duration)

        return '''def solution(*args, **kwargs):
    """This solution comes too late."""
    return "timeout"
'''

    async def analyze_and_iterate(
        self,
        challenge: ChallengeResponse,
        previous_code: str,
        error_message: str
    ) -> str:
        """Also timeout on iterations."""
        await asyncio.sleep(self.timeout_duration)
        return previous_code


class RandomAgent(BaseAgent):
    """
    Test agent that randomly succeeds or fails.

    Used for stress testing and simulating realistic agent behavior.
    Success rate is configurable.
    """

    def __init__(
        self,
        name: str = "RandomAgent",
        success_rate: float = 0.7,
        **kwargs
    ):
        """
        Initialize RandomAgent.

        Args:
            name: Agent name
            success_rate: Probability of success (0.0 to 1.0)
        """
        config = AgentConfig(
            name=name,
            model_provider="test",
            model_name="random",
            temperature=0.0,
            max_tokens=1000,
            max_iterations=3
        )
        super().__init__(config)
        self.success_rate = success_rate
        self.solution_delay = kwargs.get("solution_delay", 0.1)

        import random
        self.random = random

    async def _generate_code(self, prompt: str) -> str:
        """Generate solution that might be correct."""
        await asyncio.sleep(self.solution_delay)

        if self.random.random() < self.success_rate:
            # Return correct solution (use AlwaysPassAgent logic)
            prompt_lower = prompt.lower()

            if "fizzbuzz" in prompt_lower:
                return AlwaysPassAgent.SOLUTIONS["fizzbuzz"]
            elif "two" in prompt_lower and "sum" in prompt_lower:
                return AlwaysPassAgent.SOLUTIONS["two-sum"]
            else:
                return AlwaysPassAgent.SOLUTIONS["factorial"]
        else:
            # Return wrong solution
            return '''def solution(*args, **kwargs):
    """Random wrong answer."""
    return "WRONG"
'''

    async def analyze_and_iterate(
        self,
        challenge: ChallengeResponse,
        previous_code: str,
        error_message: str
    ) -> str:
        """Try again with different random outcome."""
        return await self._generate_code(f"Fix this: {error_message}")


class SlowAgent(BaseAgent):
    """
    Test agent that is slow but eventually succeeds.

    Used for testing performance ranking in competitions.
    """

    def __init__(self, name: str = "SlowAgent", delay: float = 2.0, **kwargs):
        """
        Initialize SlowAgent.

        Args:
            name: Agent name
            delay: How long to think before responding (seconds)
        """
        config = AgentConfig(
            name=name,
            model_provider="test",
            model_name="slow",
            temperature=0.0,
            max_tokens=1000,
            max_iterations=1
        )
        super().__init__(config)
        self.delay = delay

    async def _generate_code(self, prompt: str) -> str:
        """Generate correct solution but slowly."""
        # Simulate slow thinking
        await asyncio.sleep(self.delay)

        # Eventually return correct solution
        prompt_lower = prompt.lower()

        if "fizzbuzz" in prompt_lower:
            return AlwaysPassAgent.SOLUTIONS["fizzbuzz"]
        elif "two" in prompt_lower and "sum" in prompt_lower:
            return AlwaysPassAgent.SOLUTIONS["two-sum"]
        else:
            return AlwaysPassAgent.SOLUTIONS["factorial"]

    async def analyze_and_iterate(
        self,
        challenge: ChallengeResponse,
        previous_code: str,
        error_message: str
    ) -> str:
        """Analyze slowly."""
        await asyncio.sleep(self.delay)
        return previous_code


# ============================================================================
# Factory Function
# ============================================================================

def create_test_agent(agent_type: str, **kwargs) -> BaseAgent:
    """
    Create a test agent of the specified type.

    Args:
        agent_type: Type of test agent (pass, fail, timeout, random, slow)
        **kwargs: Additional arguments for the agent

    Returns:
        Test agent instance

    Raises:
        ValueError: If agent_type is unknown
    """
    agents = {
        "pass": AlwaysPassAgent,
        "fail": AlwaysFailAgent,
        "timeout": TimeoutAgent,
        "random": RandomAgent,
        "slow": SlowAgent,
    }

    if agent_type not in agents:
        raise ValueError(
            f"Unknown agent type: {agent_type}. "
            f"Must be one of: {', '.join(agents.keys())}"
        )

    return agents[agent_type](**kwargs)


__all__ = [
    "AlwaysPassAgent",
    "AlwaysFailAgent",
    "TimeoutAgent",
    "RandomAgent",
    "SlowAgent",
    "create_test_agent",
]
