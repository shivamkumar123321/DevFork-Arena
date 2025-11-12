"""
Test Challenges for Validation

Collection of simple challenges for testing the agent system.
These challenges have known solutions and are used to validate
that agents can correctly solve problems.
"""
from models import ChallengeResponse, TestCase, DifficultyLevel


def get_fizzbuzz_challenge() -> ChallengeResponse:
    """
    Get FizzBuzz challenge.

    Classic programming challenge:
    - Print numbers 1 to n
    - For multiples of 3, print "Fizz"
    - For multiples of 5, print "Buzz"
    - For multiples of both, print "FizzBuzz"
    """
    return ChallengeResponse(
        id="test-fizzbuzz",
        title="FizzBuzz",
        description="""Write a function that returns the FizzBuzz sequence up to n.

For each number from 1 to n:
- If divisible by both 3 and 5, add "FizzBuzz"
- Else if divisible by 3, add "Fizz"
- Else if divisible by 5, add "Buzz"
- Else add the number as a string

Return a list of strings.""",
        difficulty=DifficultyLevel.EASY,
        test_cases=[
            TestCase(
                input="15",
                expected_output='["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]',
                is_hidden=False
            ),
            TestCase(
                input="5",
                expected_output='["1", "2", "Fizz", "4", "Buzz"]',
                is_hidden=False
            ),
            TestCase(
                input="3",
                expected_output='["1", "2", "Fizz"]',
                is_hidden=False
            ),
        ],
        constraints="1 <= n <= 1000",
        time_limit=60,
        memory_limit=256,
        tags=["easy", "loops", "conditionals"],
        function_name="fizzbuzz"
    )


def get_two_sum_challenge() -> ChallengeResponse:
    """
    Get Two Sum challenge.

    Given an array of integers and a target, find two numbers
    that add up to the target.
    """
    return ChallengeResponse(
        id="test-two-sum",
        title="Two Sum",
        description="""Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.""",
        difficulty=DifficultyLevel.EASY,
        test_cases=[
            TestCase(
                input="[2,7,11,15], 9",
                expected_output="[0,1]",
                is_hidden=False
            ),
            TestCase(
                input="[3,2,4], 6",
                expected_output="[1,2]",
                is_hidden=False
            ),
            TestCase(
                input="[3,3], 6",
                expected_output="[0,1]",
                is_hidden=False
            ),
        ],
        constraints="2 <= nums.length <= 10^4, -10^9 <= nums[i] <= 10^9",
        time_limit=60,
        memory_limit=256,
        tags=["easy", "array", "hash-table"],
        function_name="two_sum"
    )


def get_reverse_string_challenge() -> ChallengeResponse:
    """Get Reverse String challenge."""
    return ChallengeResponse(
        id="test-reverse-string",
        title="Reverse String",
        description="""Write a function that reverses a string.

The input string is given as a string, and you should return the reversed string.""",
        difficulty=DifficultyLevel.EASY,
        test_cases=[
            TestCase(input='"hello"', expected_output='"olleh"', is_hidden=False),
            TestCase(input='"world"', expected_output='"dlrow"', is_hidden=False),
            TestCase(input='"a"', expected_output='"a"', is_hidden=False),
        ],
        constraints="0 <= s.length <= 1000",
        time_limit=60,
        memory_limit=256,
        tags=["easy", "string"],
        function_name="reverse_string"
    )


def get_palindrome_challenge() -> ChallengeResponse:
    """Get Palindrome Check challenge."""
    return ChallengeResponse(
        id="test-palindrome",
        title="Valid Palindrome",
        description="""A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward.

Given a string s, return true if it is a palindrome, or false otherwise.""",
        difficulty=DifficultyLevel.EASY,
        test_cases=[
            TestCase(
                input='"A man, a plan, a canal: Panama"',
                expected_output="True",
                is_hidden=False
            ),
            TestCase(
                input='"race a car"',
                expected_output="False",
                is_hidden=False
            ),
            TestCase(
                input='" "',
                expected_output="True",
                is_hidden=False
            ),
        ],
        constraints="1 <= s.length <= 1000",
        time_limit=60,
        memory_limit=256,
        tags=["easy", "string", "two-pointers"],
        function_name="is_palindrome"
    )


def get_factorial_challenge() -> ChallengeResponse:
    """Get Factorial challenge."""
    return ChallengeResponse(
        id="test-factorial",
        title="Factorial",
        description="""Write a function to calculate the factorial of a non-negative integer n.

The factorial of n (written as n!) is the product of all positive integers less than or equal to n.

For example:
- 5! = 5 × 4 × 3 × 2 × 1 = 120
- 0! = 1 (by definition)""",
        difficulty=DifficultyLevel.EASY,
        test_cases=[
            TestCase(input="5", expected_output="120", is_hidden=False),
            TestCase(input="0", expected_output="1", is_hidden=False),
            TestCase(input="1", expected_output="1", is_hidden=False),
            TestCase(input="10", expected_output="3628800", is_hidden=False),
        ],
        constraints="0 <= n <= 20",
        time_limit=60,
        memory_limit=256,
        tags=["easy", "math", "recursion"],
        function_name="factorial"
    )


def get_fibonacci_challenge() -> ChallengeResponse:
    """Get Fibonacci challenge."""
    return ChallengeResponse(
        id="test-fibonacci",
        title="Fibonacci Number",
        description="""The Fibonacci numbers, commonly denoted F(n), form a sequence where each number is the sum of the two preceding ones:

F(0) = 0, F(1) = 1
F(n) = F(n - 1) + F(n - 2), for n > 1

Given n, calculate F(n).""",
        difficulty=DifficultyLevel.EASY,
        test_cases=[
            TestCase(input="0", expected_output="0", is_hidden=False),
            TestCase(input="1", expected_output="1", is_hidden=False),
            TestCase(input="2", expected_output="1", is_hidden=False),
            TestCase(input="10", expected_output="55", is_hidden=False),
        ],
        constraints="0 <= n <= 30",
        time_limit=60,
        memory_limit=256,
        tags=["easy", "math", "dynamic-programming"],
        function_name="fibonacci"
    )


# ============================================================================
# Challenge Collections
# ============================================================================

EASY_CHALLENGES = [
    get_fizzbuzz_challenge,
    get_two_sum_challenge,
    get_reverse_string_challenge,
    get_palindrome_challenge,
    get_factorial_challenge,
    get_fibonacci_challenge,
]


def get_all_test_challenges() -> list[ChallengeResponse]:
    """Get all test challenges."""
    return [challenge_func() for challenge_func in EASY_CHALLENGES]


def get_challenge_by_id(challenge_id: str) -> ChallengeResponse:
    """
    Get a specific challenge by ID.

    Args:
        challenge_id: Challenge identifier

    Returns:
        ChallengeResponse

    Raises:
        ValueError: If challenge not found
    """
    challenges = get_all_test_challenges()
    for challenge in challenges:
        if challenge.id == challenge_id:
            return challenge

    raise ValueError(f"Challenge not found: {challenge_id}")


def get_random_challenge() -> ChallengeResponse:
    """Get a random test challenge."""
    import random
    challenge_func = random.choice(EASY_CHALLENGES)
    return challenge_func()


__all__ = [
    "get_fizzbuzz_challenge",
    "get_two_sum_challenge",
    "get_reverse_string_challenge",
    "get_palindrome_challenge",
    "get_factorial_challenge",
    "get_fibonacci_challenge",
    "get_all_test_challenges",
    "get_challenge_by_id",
    "get_random_challenge",
    "EASY_CHALLENGES",
]
