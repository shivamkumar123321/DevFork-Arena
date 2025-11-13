"""
Prompt templates for AI coding agents.

This module provides specialized prompt templates for different stages
of the challenge-solving process.
"""
from typing import Dict, List, Any, Optional
from string import Template


class PromptTemplates:
    """Collection of prompt templates for AI coding agents."""

    # Challenge Solving Prompt - Used for initial solution generation
    CHALLENGE_SOLVING_PROMPT = """You are an expert programmer competing in a coding challenge.

Challenge: {title}
Difficulty: {difficulty}

Problem Statement:
{description}

Language: {language}
Time Limit: {time_limit} seconds
Memory Limit: {memory_limit} MB

{constraints_section}

{test_cases_section}

{starter_code_section}

Instructions:
1. Analyze the problem carefully and understand all requirements
2. Consider edge cases and boundary conditions
3. Choose the most efficient algorithm and data structures
4. Write clean, readable, and well-commented code
5. Ensure your solution handles all test cases correctly
6. Return ONLY the complete, executable code without explanations

Your solution:"""

    # Iteration Prompt - Used when a solution fails and needs improvement
    ITERATION_PROMPT = """Your previous solution failed. Let's analyze what went wrong and fix it.

Challenge: {title}

Previous Code:
```{language}
{previous_code}
```

{error_section}

{failed_tests_section}

Analysis Questions:
1. What caused the error or test failure?
2. Are there edge cases that weren't handled?
3. Is the algorithm correct and efficient?
4. Are there any logic errors or off-by-one errors?
5. Did you consider all constraints?

Instructions:
Provide a corrected solution that fixes these issues. Return ONLY the complete, executable code.

Improved solution:"""

    # Detailed Analysis Prompt - For complex debugging
    DETAILED_ANALYSIS_PROMPT = """Let's perform a detailed analysis of the failed solution.

Challenge: {title}
Difficulty: {difficulty}

Problem Requirements:
{description}

Your Previous Attempt:
```{language}
{previous_code}
```

Test Results:
- Total Tests: {total_tests}
- Passed: {passed_tests}
- Failed: {failed_tests}

{detailed_failures}

Common Issues to Check:
- Off-by-one errors in loops or array indices
- Integer overflow or underflow
- Edge cases (empty input, single element, very large numbers)
- Time complexity issues (nested loops causing TLE)
- Memory usage (excessive data structures)
- Incorrect algorithm choice

Step-by-step debugging:
1. Trace through the failed test case manually
2. Identify where the output diverges from expected
3. Fix the specific issue
4. Verify the fix doesn't break other cases

Provide the corrected code:"""

    # Code Optimization Prompt - For improving working solutions
    OPTIMIZATION_PROMPT = """Your solution works but can be optimized.

Challenge: {title}
Current Execution Time: {execution_time}s
Time Limit: {time_limit}s

Current Code:
```{language}
{current_code}
```

Optimization Opportunities:
{optimization_hints}

Goal: Improve time complexity or reduce execution time while maintaining correctness.

Provide an optimized version:"""

    # Error Recovery Prompt - When facing syntax or runtime errors
    ERROR_RECOVERY_PROMPT = """Your code encountered an error during execution.

Error Type: {error_type}
Error Message: {error_message}

Code with Error:
```{language}
{error_code}
```

{stack_trace_section}

Common fixes for this error:
{error_hints}

Provide corrected code:"""


class PromptBuilder:
    """
    Helper class to build formatted prompts from templates.
    """

    @staticmethod
    def build_challenge_prompt(
        title: str,
        difficulty: str,
        description: str,
        language: str = "python",
        time_limit: int = 60,
        memory_limit: int = 256,
        constraints: Optional[str] = None,
        test_cases: Optional[List[Dict[str, Any]]] = None,
        starter_code: Optional[str] = None
    ) -> str:
        """
        Build a challenge-solving prompt.

        Args:
            title: Challenge title
            difficulty: Difficulty level (easy, medium, hard)
            description: Problem description
            language: Programming language
            time_limit: Time limit in seconds
            memory_limit: Memory limit in MB
            constraints: Problem constraints
            test_cases: List of test cases (visible ones)
            starter_code: Optional starter code template

        Returns:
            Formatted prompt string
        """
        # Build constraints section
        constraints_section = ""
        if constraints:
            constraints_section = f"\nConstraints:\n{constraints}"

        # Build test cases section
        test_cases_section = ""
        if test_cases:
            test_cases_section = "\nExample Test Cases:\n"
            for i, tc in enumerate(test_cases[:3], 1):  # Show first 3
                if not tc.get('is_hidden', False):
                    test_cases_section += f"\nTest {i}:\n"
                    test_cases_section += f"  Input: {tc['input']}\n"
                    test_cases_section += f"  Expected Output: {tc['expected_output']}\n"

        # Build starter code section
        starter_code_section = ""
        if starter_code:
            starter_code_section = f"\nStarter Code:\n```{language}\n{starter_code}\n```"

        return PromptTemplates.CHALLENGE_SOLVING_PROMPT.format(
            title=title,
            difficulty=difficulty,
            description=description,
            language=language,
            time_limit=time_limit,
            memory_limit=memory_limit,
            constraints_section=constraints_section,
            test_cases_section=test_cases_section,
            starter_code_section=starter_code_section
        )

    @staticmethod
    def build_iteration_prompt(
        title: str,
        previous_code: str,
        error_message: Optional[str] = None,
        failed_tests: Optional[List[Dict[str, Any]]] = None,
        language: str = "python"
    ) -> str:
        """
        Build an iteration prompt for failed solutions.

        Args:
            title: Challenge title
            previous_code: Code from previous attempt
            error_message: Error message if execution failed
            failed_tests: List of failed test cases
            language: Programming language

        Returns:
            Formatted prompt string
        """
        # Build error section
        error_section = ""
        if error_message:
            error_section = f"Execution Error:\n{error_message}\n"

        # Build failed tests section
        failed_tests_section = ""
        if failed_tests:
            failed_tests_section = "Failed Test Cases:\n"
            for i, test in enumerate(failed_tests[:3], 1):  # Show first 3 failures
                failed_tests_section += f"\nTest {i}:\n"
                failed_tests_section += f"  Input: {test.get('input', 'N/A')}\n"
                failed_tests_section += f"  Expected: {test.get('expected', 'N/A')}\n"
                failed_tests_section += f"  Got: {test.get('actual', 'N/A')}\n"
                if 'error' in test:
                    failed_tests_section += f"  Error: {test['error']}\n"

        return PromptTemplates.ITERATION_PROMPT.format(
            title=title,
            language=language,
            previous_code=previous_code,
            error_section=error_section,
            failed_tests_section=failed_tests_section
        )

    @staticmethod
    def build_detailed_analysis_prompt(
        title: str,
        difficulty: str,
        description: str,
        previous_code: str,
        total_tests: int,
        passed_tests: int,
        failed_tests: int,
        failures: List[Dict[str, Any]],
        language: str = "python"
    ) -> str:
        """
        Build a detailed analysis prompt for complex debugging.

        Args:
            title: Challenge title
            difficulty: Difficulty level
            description: Problem description
            previous_code: Code from previous attempt
            total_tests: Total number of tests
            passed_tests: Number of passed tests
            failed_tests: Number of failed tests
            failures: Detailed failure information
            language: Programming language

        Returns:
            Formatted prompt string
        """
        # Build detailed failures section
        detailed_failures = "Detailed Failures:\n"
        for i, failure in enumerate(failures[:5], 1):  # Show first 5
            detailed_failures += f"\nFailure {i}:\n"
            for key, value in failure.items():
                detailed_failures += f"  {key}: {value}\n"

        return PromptTemplates.DETAILED_ANALYSIS_PROMPT.format(
            title=title,
            difficulty=difficulty,
            description=description,
            language=language,
            previous_code=previous_code,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            detailed_failures=detailed_failures
        )

    @staticmethod
    def build_optimization_prompt(
        title: str,
        current_code: str,
        execution_time: float,
        time_limit: int,
        optimization_hints: Optional[List[str]] = None,
        language: str = "python"
    ) -> str:
        """
        Build an optimization prompt for working but slow solutions.

        Args:
            title: Challenge title
            current_code: Current working code
            execution_time: Current execution time
            time_limit: Time limit
            optimization_hints: List of optimization suggestions
            language: Programming language

        Returns:
            Formatted prompt string
        """
        hints_text = ""
        if optimization_hints:
            hints_text = "\n".join(f"- {hint}" for hint in optimization_hints)
        else:
            hints_text = """- Consider using more efficient data structures (hash maps, sets)
- Reduce nested loops (can it be O(n) instead of O(n²)?)
- Use early termination when possible
- Cache repeated calculations
- Consider built-in functions that are optimized"""

        return PromptTemplates.OPTIMIZATION_PROMPT.format(
            title=title,
            current_code=current_code,
            execution_time=execution_time,
            time_limit=time_limit,
            optimization_hints=hints_text,
            language=language
        )

    @staticmethod
    def build_error_recovery_prompt(
        error_type: str,
        error_message: str,
        error_code: str,
        stack_trace: Optional[str] = None,
        language: str = "python"
    ) -> str:
        """
        Build an error recovery prompt.

        Args:
            error_type: Type of error (SyntaxError, RuntimeError, etc.)
            error_message: Error message
            error_code: Code that caused the error
            stack_trace: Optional stack trace
            language: Programming language

        Returns:
            Formatted prompt string
        """
        stack_trace_section = ""
        if stack_trace:
            stack_trace_section = f"\nStack Trace:\n{stack_trace}"

        # Error-specific hints
        error_hints_map = {
            "SyntaxError": [
                "Check for missing colons, parentheses, or brackets",
                "Verify proper indentation",
                "Look for unclosed strings or comments"
            ],
            "IndexError": [
                "Check array/list bounds",
                "Verify loop ranges",
                "Check for off-by-one errors"
            ],
            "KeyError": [
                "Verify dictionary keys exist before accessing",
                "Use .get() method with default values",
                "Check for typos in key names"
            ],
            "TypeError": [
                "Verify variable types match expected operations",
                "Check function argument types",
                "Ensure proper type conversions"
            ],
            "ZeroDivisionError": [
                "Check for division by zero",
                "Add validation for divisor",
                "Handle edge cases where denominator is 0"
            ]
        }

        hints = error_hints_map.get(error_type, [
            "Review the error message carefully",
            "Check the line mentioned in the error",
            "Verify variable values at the point of error"
        ])

        error_hints = "\n".join(f"- {hint}" for hint in hints)

        return PromptTemplates.ERROR_RECOVERY_PROMPT.format(
            error_type=error_type,
            error_message=error_message,
            error_code=error_code,
            stack_trace_section=stack_trace_section,
            error_hints=error_hints,
            language=language
        )


# Convenience functions for quick prompt building
def format_challenge_prompt(**kwargs) -> str:
    """Quick challenge prompt builder."""
    return PromptBuilder.build_challenge_prompt(**kwargs)


def format_iteration_prompt(**kwargs) -> str:
    """Quick iteration prompt builder."""
    return PromptBuilder.build_iteration_prompt(**kwargs)


def format_analysis_prompt(**kwargs) -> str:
    """Quick analysis prompt builder."""
    return PromptBuilder.build_detailed_analysis_prompt(**kwargs)


def format_optimization_prompt(**kwargs) -> str:
    """Quick optimization prompt builder."""
    return PromptBuilder.build_optimization_prompt(**kwargs)


def format_error_recovery_prompt(**kwargs) -> str:
    """Quick error recovery prompt builder."""
    return PromptBuilder.build_error_recovery_prompt(**kwargs)
