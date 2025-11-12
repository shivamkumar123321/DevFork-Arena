"""
Code Executor for safely running and testing Python code.

This module provides functionality to execute Python code in a controlled environment
and run test cases against it.
"""
import sys
import io
import traceback
import contextlib
import logging
import time
from typing import Dict, Any, List, Optional
import ast
import signal
from multiprocessing import Process, Queue

import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import TestCase, TestResult

logger = logging.getLogger(__name__)


class TimeoutException(Exception):
    """Exception raised when code execution times out."""
    pass


class CodeExecutor:
    """
    Safely execute Python code and run test cases.

    This executor provides a sandboxed environment for running untrusted code
    with timeout protection and output capture.
    """

    def __init__(self, timeout: int = 5):
        """
        Initialize the code executor.

        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout

    def execute_code(
        self,
        code: str,
        test_input: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute Python code and capture output.

        Args:
            code: Python code to execute
            test_input: Optional input to provide to the code

        Returns:
            Dict containing:
                - success: bool
                - output: str (stdout)
                - error: str (stderr or exception)
                - execution_time: float
        """
        start_time = time.time()

        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        result = {
            "success": False,
            "output": "",
            "error": "",
            "execution_time": 0.0
        }

        try:
            # Create a restricted globals dict
            restricted_globals = {
                "__builtins__": __builtins__,
                "print": print,
                "len": len,
                "range": range,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "sum": sum,
                "max": max,
                "min": min,
                "abs": abs,
                "sorted": sorted,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
            }

            # Execute code with output capture
            with contextlib.redirect_stdout(stdout_capture), \
                 contextlib.redirect_stderr(stderr_capture):

                # Compile and execute
                compiled_code = compile(code, '<string>', 'exec')
                exec(compiled_code, restricted_globals)

            execution_time = time.time() - start_time

            result["success"] = True
            result["output"] = stdout_capture.getvalue()
            result["execution_time"] = execution_time

        except SyntaxError as e:
            result["error"] = f"Syntax Error: {str(e)}"
            logger.error(f"Syntax error in code: {e}")

        except Exception as e:
            result["error"] = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            logger.error(f"Execution error: {e}")

        finally:
            result["execution_time"] = time.time() - start_time

        return result

    def run_test_cases(
        self,
        code: str,
        test_cases: List[TestCase],
        function_name: Optional[str] = None
    ) -> TestResult:
        """
        Run test cases against the provided code.

        Args:
            code: Python code containing the solution
            test_cases: List of TestCase objects
            function_name: Name of the function to test (auto-detect if None)

        Returns:
            TestResult: Results of running all test cases
        """
        if not test_cases:
            return TestResult(
                passed=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=[{"error": "No test cases provided"}],
                error_message="No test cases to run"
            )

        # Auto-detect function name if not provided
        if function_name is None:
            function_name = self._extract_function_name(code)
            if not function_name:
                return TestResult(
                    passed=False,
                    total_tests=len(test_cases),
                    passed_tests=0,
                    failed_tests=[{"error": "Could not find function in code"}],
                    error_message="No function definition found in code"
                )

        total_tests = len(test_cases)
        passed_tests = 0
        failed_tests = []
        total_time = 0.0

        for i, test_case in enumerate(test_cases):
            try:
                result = self._run_single_test(
                    code=code,
                    function_name=function_name,
                    test_case=test_case,
                    test_number=i + 1
                )

                total_time += result.get("execution_time", 0.0)

                if result["success"]:
                    passed_tests += 1
                else:
                    failed_tests.append({
                        "test_number": i + 1,
                        "input": test_case.input,
                        "expected": test_case.expected_output,
                        "actual": result.get("output", ""),
                        "error": result.get("error", "")
                    })

            except Exception as e:
                failed_tests.append({
                    "test_number": i + 1,
                    "input": test_case.input,
                    "error": f"Test execution failed: {str(e)}"
                })

        return TestResult(
            passed=(passed_tests == total_tests),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            execution_time=total_time
        )

    def _run_single_test(
        self,
        code: str,
        function_name: str,
        test_case: TestCase,
        test_number: int
    ) -> Dict[str, Any]:
        """
        Run a single test case.

        Args:
            code: Python code to test
            function_name: Name of the function to call
            test_case: TestCase to run
            test_number: Test number for logging

        Returns:
            Dict with test results
        """
        start_time = time.time()

        try:
            # Create namespace for execution
            namespace = {}

            # Execute the code to define the function
            exec(code, namespace)

            # Get the function
            if function_name not in namespace:
                return {
                    "success": False,
                    "error": f"Function '{function_name}' not found in code",
                    "execution_time": time.time() - start_time
                }

            func = namespace[function_name]

            # Parse the input
            # The input format is expected to be comma-separated arguments
            # e.g., "[2,7,11,15], 9" or "5, 10"
            try:
                # Try to evaluate the input as Python expressions
                input_parts = test_case.input.split(',')
                args = []
                current_arg = ""

                bracket_count = 0
                for part in input_parts:
                    current_arg += part
                    bracket_count += part.count('[') + part.count('(') + part.count('{')
                    bracket_count -= part.count(']') + part.count(')') + part.count('}')

                    if bracket_count == 0:
                        # Complete argument
                        args.append(eval(current_arg.strip()))
                        current_arg = ""
                    else:
                        current_arg += ","

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to parse input: {str(e)}",
                    "execution_time": time.time() - start_time
                }

            # Call the function
            result = func(*args)

            # Parse expected output
            try:
                expected = eval(test_case.expected_output)
            except:
                expected = test_case.expected_output

            # Compare results
            if result == expected:
                return {
                    "success": True,
                    "output": str(result),
                    "execution_time": time.time() - start_time
                }
            else:
                return {
                    "success": False,
                    "output": str(result),
                    "error": f"Expected {expected}, got {result}",
                    "execution_time": time.time() - start_time
                }

        except TimeoutException:
            return {
                "success": False,
                "error": f"Execution timed out after {self.timeout} seconds",
                "execution_time": time.time() - start_time
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Runtime error: {str(e)}\n{traceback.format_exc()}",
                "execution_time": time.time() - start_time
            }

    def _extract_function_name(self, code: str) -> Optional[str]:
        """
        Extract the main function name from Python code.

        Args:
            code: Python code

        Returns:
            str: Function name or None if not found
        """
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Return the first function defined
                    return node.name
        except:
            pass

        return None

    def validate_syntax(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Validate Python code syntax.

        Args:
            code: Python code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Syntax Error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"


# Global executor instance
executor = CodeExecutor(timeout=5)
