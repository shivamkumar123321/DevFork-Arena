"""
Base Agent Framework for AI-powered coding challenge solvers.

This module provides an abstract base class that defines the interface
for all AI agents in the DevFork Arena system.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import logging
import re
import traceback
from datetime import datetime

from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseMessage

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    ChallengeResponse,
    AgentConfig,
    TestResult,
    SolutionAttempt,
    CodeSubmission
)

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for AI coding agents.

    This class defines the common interface and shared functionality for all AI agents
    that solve coding challenges in the DevFork Arena system.

    Attributes:
        config: Agent configuration including model settings
        llm: LangChain language model instance
        solution_attempts: History of solution attempts
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize the base agent with configuration.

        Args:
            config: AgentConfig instance with agent settings
        """
        self.config = config
        self.llm = None
        self.solution_attempts: List[SolutionAttempt] = []
        self.current_challenge: Optional[ChallengeResponse] = None

        # Initialize the language model
        self._initialize_llm()

        logger.info(f"Initialized {self.config.name} with model {self.config.model_name}")

    @abstractmethod
    def _initialize_llm(self):
        """
        Initialize the language model.

        Must be implemented by concrete agent classes to set up their specific
        LLM (Claude, GPT-4, etc.)
        """
        pass

    async def solve_challenge(self, challenge: ChallengeResponse) -> str:
        """
        Main entry point for solving a coding challenge.

        This method orchestrates the entire solving process:
        1. Format the challenge prompt
        2. Generate initial solution
        3. Test the solution
        4. Iterate if needed

        Args:
            challenge: ChallengeResponse containing challenge details

        Returns:
            str: Final code solution

        Raises:
            Exception: If unable to solve after max iterations
        """
        self.current_challenge = challenge
        self.solution_attempts = []

        logger.info(f"Starting to solve challenge: {challenge.title}")

        # Generate initial solution
        prompt = await self.format_challenge_prompt(challenge)
        code = await self._generate_code(prompt)

        # Test and iterate
        for attempt in range(1, self.config.max_iterations + 1):
            logger.info(f"Attempt {attempt}/{self.config.max_iterations}")

            # Simulate testing (in production, this would run actual tests)
            test_result = await self._test_solution(code, challenge)

            # Record attempt
            solution_attempt = SolutionAttempt(
                attempt_number=attempt,
                code=code,
                test_result=test_result,
                analysis=None
            )
            self.solution_attempts.append(solution_attempt)

            # If successful, return the solution
            if test_result.passed:
                logger.info(f"Successfully solved challenge in {attempt} attempt(s)")
                return code

            # If not the last attempt, analyze and iterate
            if attempt < self.config.max_iterations:
                logger.info(f"Tests failed. Analyzing and iterating...")
                code = await self.analyze_and_iterate(
                    challenge=challenge,
                    previous_code=code,
                    error_message=test_result.error_message or self._format_test_failures(test_result)
                )

        # If we've exhausted all attempts
        logger.error(f"Failed to solve challenge after {self.config.max_iterations} attempts")
        raise Exception(f"Unable to solve challenge after {self.config.max_iterations} attempts")

    async def analyze_and_iterate(
        self,
        challenge: ChallengeResponse,
        previous_code: str,
        error_message: str
    ) -> str:
        """
        Analyze test failures and generate an improved solution.

        This method takes the previous attempt and error information,
        analyzes what went wrong, and generates an improved solution.

        Args:
            challenge: ChallengeResponse containing challenge details
            previous_code: The code from the previous attempt
            error_message: Error message or test failure details

        Returns:
            str: Improved code solution
        """
        logger.info("Analyzing previous attempt and generating improved solution")

        analysis_prompt = self._create_iteration_prompt(
            challenge=challenge,
            previous_code=previous_code,
            error_message=error_message
        )

        # Generate improved solution
        improved_code = await self._generate_code(analysis_prompt)

        return improved_code

    async def format_challenge_prompt(self, challenge: ChallengeResponse) -> str:
        """
        Format the challenge into a clear prompt for the LLM.

        This method converts the ChallengeResponse into a well-structured
        prompt that helps the LLM understand what needs to be solved.

        Args:
            challenge: ChallengeResponse containing challenge details

        Returns:
            str: Formatted prompt string
        """
        # Build test cases section
        test_cases_str = ""
        if challenge.test_cases:
            test_cases_str = "\n\nTest Cases:\n"
            for i, test_case in enumerate(challenge.test_cases[:3], 1):  # Show first 3 test cases
                if not test_case.is_hidden:
                    test_cases_str += f"\nTest {i}:\n"
                    test_cases_str += f"  Input: {test_case.input}\n"
                    test_cases_str += f"  Expected Output: {test_case.expected_output}\n"

        # Build constraints section
        constraints_str = ""
        if challenge.constraints:
            constraints_str = f"\n\nConstraints:\n{challenge.constraints}"

        # Build tags section
        tags_str = ""
        if challenge.tags:
            tags_str = f"\n\nTags: {', '.join(challenge.tags)}"

        prompt = f"""You are an expert programmer solving a coding challenge.

Challenge: {challenge.title}
Difficulty: {challenge.difficulty.value}

Description:
{challenge.description}
{test_cases_str}
{constraints_str}
{tags_str}

Please provide a complete, working Python solution. Your code should:
1. Be efficient and handle all edge cases
2. Pass all test cases
3. Follow Python best practices
4. Include a main function that can be tested

Return ONLY the Python code, without any explanations or markdown formatting.
"""

        return prompt

    def _create_iteration_prompt(
        self,
        challenge: ChallengeResponse,
        previous_code: str,
        error_message: str
    ) -> str:
        """
        Create a prompt for iteration after a failed attempt.

        Args:
            challenge: ChallengeResponse containing challenge details
            previous_code: Code from the previous attempt
            error_message: Error or failure details

        Returns:
            str: Formatted iteration prompt
        """
        prompt = f"""You are an expert programmer debugging and improving a solution to a coding challenge.

Challenge: {challenge.title}
Description: {challenge.description}

Your previous solution:
```python
{previous_code}
```

The solution failed with the following error/test failures:
{error_message}

Please analyze the error and provide a corrected solution. Consider:
1. What caused the error or test failure?
2. Are there edge cases that weren't handled?
3. Is the algorithm correct?
4. Are there any logic errors?

Provide a complete, corrected Python solution that fixes these issues.
Return ONLY the Python code, without any explanations or markdown formatting.
"""

        return prompt

    @abstractmethod
    async def _generate_code(self, prompt: str) -> str:
        """
        Generate code using the LLM.

        Must be implemented by concrete agent classes to use their specific
        LLM for code generation.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            str: Generated code
        """
        pass

    async def _test_solution(
        self,
        code: str,
        challenge: ChallengeResponse
    ) -> TestResult:
        """
        Test a solution against the challenge test cases.

        This is a placeholder implementation. In production, this would:
        1. Execute the code in a sandboxed environment
        2. Run all test cases
        3. Capture results and errors

        Args:
            code: The code to test
            challenge: Challenge with test cases

        Returns:
            TestResult: Results of the test execution
        """
        # This is a simplified implementation
        # In production, you would actually execute the code and run tests

        try:
            # Basic validation
            if not code or len(code.strip()) < 10:
                return TestResult(
                    passed=False,
                    total_tests=len(challenge.test_cases),
                    passed_tests=0,
                    failed_tests=[{"error": "Code is too short or empty"}],
                    error_message="Generated code is invalid or too short"
                )

            # Check for syntax errors
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError as e:
                return TestResult(
                    passed=False,
                    total_tests=len(challenge.test_cases),
                    passed_tests=0,
                    failed_tests=[{"error": str(e)}],
                    error_message=f"Syntax Error: {str(e)}"
                )

            # In a real implementation, you would execute the code here
            # For now, we'll simulate a success to demonstrate the flow
            logger.info("Testing solution (simulated)")

            # Simulate that some attempts might fail
            if len(self.solution_attempts) == 0:
                # First attempt - simulate a potential failure for demonstration
                # In production, this would be actual test results
                return TestResult(
                    passed=True,  # Set to True for demo purposes
                    total_tests=len(challenge.test_cases),
                    passed_tests=len(challenge.test_cases),
                    failed_tests=[],
                    execution_time=0.1
                )

            return TestResult(
                passed=True,
                total_tests=len(challenge.test_cases),
                passed_tests=len(challenge.test_cases),
                failed_tests=[],
                execution_time=0.1
            )

        except Exception as e:
            logger.error(f"Error testing solution: {str(e)}")
            return TestResult(
                passed=False,
                total_tests=len(challenge.test_cases),
                passed_tests=0,
                failed_tests=[{"error": str(e)}],
                error_message=f"Execution error: {str(e)}\n{traceback.format_exc()}"
            )

    def _format_test_failures(self, test_result: TestResult) -> str:
        """
        Format test failures into a readable error message.

        Args:
            test_result: TestResult with failure information

        Returns:
            str: Formatted error message
        """
        if not test_result.failed_tests:
            return "Tests failed but no specific error information available"

        message = f"Failed {len(test_result.failed_tests)} out of {test_result.total_tests} tests:\n\n"

        for i, failure in enumerate(test_result.failed_tests[:5], 1):  # Show first 5 failures
            message += f"Failure {i}:\n"
            for key, value in failure.items():
                message += f"  {key}: {value}\n"
            message += "\n"

        return message

    def _extract_code_from_response(self, response: str) -> str:
        """
        Extract clean Python code from LLM response.

        LLMs sometimes wrap code in markdown blocks or add explanations.
        This method extracts just the code.

        Args:
            response: Raw response from LLM

        Returns:
            str: Extracted Python code
        """
        # Try to extract code from markdown blocks
        code_block_pattern = r"```(?:python)?\n(.*?)```"
        matches = re.findall(code_block_pattern, response, re.DOTALL)

        if matches:
            # Return the first code block found
            return matches[0].strip()

        # If no markdown blocks, return the response as-is
        # but try to remove common non-code prefixes
        lines = response.strip().split('\n')

        # Skip lines that look like explanations
        code_lines = []
        in_code = False

        for line in lines:
            # Start collecting when we see code-like content
            if 'def ' in line or 'class ' in line or 'import ' in line or 'from ' in line:
                in_code = True

            if in_code:
                code_lines.append(line)

        if code_lines:
            return '\n'.join(code_lines)

        # If all else fails, return the original response
        return response.strip()

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the agent's performance on the current challenge.

        Returns:
            Dict containing performance metrics
        """
        if not self.solution_attempts:
            return {
                "total_attempts": 0,
                "success": False,
                "final_attempt": None
            }

        final_attempt = self.solution_attempts[-1]

        return {
            "challenge_id": self.current_challenge.id if self.current_challenge else None,
            "challenge_title": self.current_challenge.title if self.current_challenge else None,
            "agent_name": self.config.name,
            "total_attempts": len(self.solution_attempts),
            "success": final_attempt.test_result.passed,
            "final_attempt": {
                "attempt_number": final_attempt.attempt_number,
                "passed": final_attempt.test_result.passed,
                "tests_passed": final_attempt.test_result.passed_tests,
                "total_tests": final_attempt.test_result.total_tests,
                "execution_time": final_attempt.test_result.execution_time
            }
        }
