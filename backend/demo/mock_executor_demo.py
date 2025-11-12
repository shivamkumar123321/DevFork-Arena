"""
Mock Code Executor Demo

Demonstrates the MockCodeExecutor for testing and development
without actually executing code. Useful for:
- Testing agent logic without code execution overhead
- Development when Docker sandboxing is not available
- Reproducible testing with controlled randomness
"""
import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import TestCase
from agents import MockCodeExecutor, mock_executor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_basic_mock_execution():
    """Demonstrate basic mock code execution."""
    print("\n" + "="*60)
    print("BASIC MOCK EXECUTION DEMO")
    print("="*60 + "\n")

    # Create mock executor with 80% success rate
    executor = MockCodeExecutor(success_rate=0.8, random_seed=42)

    sample_code = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
"""

    print("Sample Code:")
    print(sample_code)
    print("\nSimulating execution...")

    result = executor.execute_code(sample_code)

    print(f"\nResult:")
    print(f"  Success: {result['success']}")
    print(f"  Output: {result.get('output', 'N/A')}")
    print(f"  Error: {result.get('error', 'None')}")
    print(f"  Execution Time: {result['execution_time']:.2f}s")


def demo_test_cases():
    """Demonstrate running test cases with mock executor."""
    print("\n" + "="*60)
    print("MOCK TEST CASES DEMO")
    print("="*60 + "\n")

    # Use global mock executor
    test_cases = [
        TestCase(input="[2,7,11,15], 9", expected_output="[0,1]", is_hidden=False),
        TestCase(input="[3,2,4], 6", expected_output="[1,2]", is_hidden=False),
        TestCase(input="[3,3], 6", expected_output="[0,1]", is_hidden=False),
    ]

    sample_code = """
def solution(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""

    print(f"Running {len(test_cases)} test cases...")
    print("(Results are randomized based on success_rate)\n")

    result = mock_executor.run_test_cases(sample_code, test_cases)

    print(f"Test Results:")
    print(f"  Passed: {result.passed}")
    print(f"  Tests Passed: {result.passed_tests}/{result.total_tests}")
    print(f"  Execution Time: {result.execution_time:.2f}s")

    if result.failed_tests:
        print(f"\n  Failed Tests:")
        for failure in result.failed_tests:
            print(f"    - Test {failure.get('test_number', '?')}: {failure.get('error', 'Unknown error')}")


def demo_syntax_validation():
    """Demonstrate syntax validation (actually works)."""
    print("\n" + "="*60)
    print("SYNTAX VALIDATION DEMO")
    print("="*60 + "\n")

    executor = MockCodeExecutor()

    # Valid code
    valid_code = "def hello():\n    print('Hello')"
    is_valid, error = executor.validate_syntax(valid_code)
    print(f"Valid Code: {is_valid}, Error: {error}")

    # Invalid code
    invalid_code = "def hello(\n    print('Hello')"
    is_valid, error = executor.validate_syntax(invalid_code)
    print(f"Invalid Code: {is_valid}, Error: {error}")


def demo_configurable_success_rate():
    """Demonstrate adjusting success rate."""
    print("\n" + "="*60)
    print("CONFIGURABLE SUCCESS RATE DEMO")
    print("="*60 + "\n")

    executor = MockCodeExecutor(success_rate=0.5, random_seed=123)

    test_cases = [
        TestCase(input="test1", expected_output="output1"),
        TestCase(input="test2", expected_output="output2"),
        TestCase(input="test3", expected_output="output3"),
    ]

    code = "def test(): pass"

    print("Testing with 50% success rate:")
    result = executor.run_test_cases(code, test_cases)
    print(f"  Passed: {result.passed_tests}/{result.total_tests}")

    # Change success rate
    executor.set_success_rate(0.9)
    print("\nTesting with 90% success rate:")
    result = executor.run_test_cases(code, test_cases)
    print(f"  Passed: {result.passed_tests}/{result.total_tests}")

    # Change to 100% success
    executor.set_success_rate(1.0)
    print("\nTesting with 100% success rate:")
    result = executor.run_test_cases(code, test_cases)
    print(f"  Passed: {result.passed_tests}/{result.total_tests}")


def demo_reproducible_results():
    """Demonstrate reproducible results with seed."""
    print("\n" + "="*60)
    print("REPRODUCIBLE RESULTS DEMO")
    print("="*60 + "\n")

    test_cases = [
        TestCase(input="test", expected_output="output")
    ]

    code = "def test(): pass"

    print("Running with seed=42 (multiple times):")
    for i in range(3):
        executor = MockCodeExecutor(success_rate=0.7, random_seed=42)
        result = executor.run_test_cases(code, test_cases)
        print(f"  Run {i+1}: Passed={result.passed}")

    print("\nRunning without seed (random each time):")
    for i in range(3):
        executor = MockCodeExecutor(success_rate=0.7)
        result = executor.run_test_cases(code, test_cases)
        print(f"  Run {i+1}: Passed={result.passed}")


def demo_realistic_errors():
    """Demonstrate realistic error simulation."""
    print("\n" + "="*60)
    print("REALISTIC ERROR SIMULATION DEMO")
    print("="*60 + "\n")

    executor = MockCodeExecutor(success_rate=0.0, random_seed=456)  # Always fail

    code = "def buggy_function(): pass"

    print("Simulating multiple executions to see different errors:")
    for i in range(5):
        result = executor.execute_code(code)
        if not result['success']:
            print(f"  Error {i+1}: {result['error']}")


def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("MockCodeExecutor Demonstration")
    print("="*60)
    print("\nThis demo shows how to use MockCodeExecutor for testing")
    print("without actually executing code.\n")

    print("Choose a demo to run:\n")
    print("1. Basic Mock Execution")
    print("2. Test Cases with Mock Executor")
    print("3. Syntax Validation")
    print("4. Configurable Success Rate")
    print("5. Reproducible Results with Seed")
    print("6. Realistic Error Simulation")
    print("7. Run All Demos")
    print("0. Exit\n")

    choice = input("Enter your choice (0-7): ").strip()

    if choice == "1":
        demo_basic_mock_execution()
    elif choice == "2":
        demo_test_cases()
    elif choice == "3":
        demo_syntax_validation()
    elif choice == "4":
        demo_configurable_success_rate()
    elif choice == "5":
        demo_reproducible_results()
    elif choice == "6":
        demo_realistic_errors()
    elif choice == "7":
        demo_basic_mock_execution()
        demo_test_cases()
        demo_syntax_validation()
        demo_configurable_success_rate()
        demo_reproducible_results()
        demo_realistic_errors()
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
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)
