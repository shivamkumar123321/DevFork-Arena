"""
Data models and schemas for the DevFork Arena application.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class DifficultyLevel(str, Enum):
    """Challenge difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ChallengeStatus(str, Enum):
    """Status of a challenge"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"


class TestCase(BaseModel):
    """Individual test case for a challenge"""
    input: str = Field(..., description="Test case input")
    expected_output: str = Field(..., description="Expected output")
    is_hidden: bool = Field(default=False, description="Whether this is a hidden test case")


class ChallengeResponse(BaseModel):
    """Challenge data structure"""
    id: str = Field(..., description="Unique challenge identifier")
    title: str = Field(..., description="Challenge title")
    description: str = Field(..., description="Detailed challenge description")
    difficulty: DifficultyLevel = Field(..., description="Challenge difficulty level")
    test_cases: List[TestCase] = Field(default_factory=list, description="Test cases for validation")
    constraints: Optional[str] = Field(None, description="Additional constraints")
    time_limit: Optional[int] = Field(60, description="Time limit in seconds")
    memory_limit: Optional[int] = Field(256, description="Memory limit in MB")
    tags: List[str] = Field(default_factory=list, description="Challenge tags/categories")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "challenge-001",
                "title": "Two Sum",
                "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
                "difficulty": "easy",
                "test_cases": [
                    {"input": "[2,7,11,15], 9", "expected_output": "[0,1]", "is_hidden": False},
                    {"input": "[3,2,4], 6", "expected_output": "[1,2]", "is_hidden": False}
                ],
                "constraints": "2 <= nums.length <= 10^4",
                "time_limit": 60,
                "memory_limit": 256,
                "tags": ["array", "hash-table"]
            }
        }


class AgentConfig(BaseModel):
    """Configuration for an AI agent"""
    name: str = Field(..., description="Agent name")
    model_provider: str = Field(..., description="Model provider (anthropic, openai)")
    model_name: str = Field(..., description="Specific model name")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: int = Field(4096, ge=1, le=100000, description="Maximum tokens to generate")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")
    max_iterations: int = Field(3, ge=1, le=10, description="Maximum retry attempts for solving")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Claude Solver",
                "model_provider": "anthropic",
                "model_name": "claude-3-5-sonnet-20241022",
                "temperature": 0.7,
                "max_tokens": 4096,
                "max_iterations": 3
            }
        }


class CodeSubmission(BaseModel):
    """Code submission for a challenge"""
    challenge_id: str = Field(..., description="Challenge identifier")
    agent_id: str = Field(..., description="Agent identifier")
    code: str = Field(..., description="Submitted code")
    language: str = Field(default="python", description="Programming language")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Submission timestamp")


class TestResult(BaseModel):
    """Result of running test cases"""
    passed: bool = Field(..., description="Whether all tests passed")
    total_tests: int = Field(..., description="Total number of tests")
    passed_tests: int = Field(..., description="Number of passed tests")
    failed_tests: List[Dict[str, Any]] = Field(default_factory=list, description="Details of failed tests")
    error_message: Optional[str] = Field(None, description="Error message if execution failed")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")


class SolutionAttempt(BaseModel):
    """Record of a solution attempt"""
    attempt_number: int = Field(..., description="Attempt number")
    code: str = Field(..., description="Code submitted in this attempt")
    test_result: TestResult = Field(..., description="Test result")
    analysis: Optional[str] = Field(None, description="Agent's analysis of the attempt")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Attempt timestamp")


class AgentPerformance(BaseModel):
    """Agent performance metrics"""
    agent_id: str = Field(..., description="Agent identifier")
    agent_name: str = Field(..., description="Agent name")
    total_challenges: int = Field(0, description="Total challenges attempted")
    challenges_solved: int = Field(0, description="Challenges successfully solved")
    success_rate: float = Field(0.0, description="Success rate percentage")
    average_attempts: float = Field(0.0, description="Average attempts per challenge")
    average_time: float = Field(0.0, description="Average time per challenge in seconds")
    total_score: int = Field(0, description="Total score accumulated")


class SubmissionStatus(str, Enum):
    """Submission status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"


class CompetitionStatus(str, Enum):
    """Competition status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AgentRecord(BaseModel):
    """Agent record in database"""
    id: UUID = Field(default_factory=uuid4, description="Agent unique identifier")
    name: str = Field(..., description="Agent name")
    model_provider: str = Field(..., description="Model provider (openai, anthropic)")
    model_name: str = Field(..., description="Specific model name")
    temperature: float = Field(0.7, description="Model temperature")
    max_tokens: int = Field(4096, description="Maximum tokens")
    max_iterations: int = Field(3, description="Maximum solution attempts")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    is_active: bool = Field(True, description="Whether agent is active")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "GPT-4 Solver",
                "model_provider": "openai",
                "model_name": "gpt-4-turbo-preview",
                "temperature": 0.7,
                "max_tokens": 4096,
                "max_iterations": 3
            }
        }


class SubmissionResponse(BaseModel):
    """Submission response"""
    id: UUID = Field(default_factory=uuid4, description="Submission unique identifier")
    competition_id: UUID = Field(..., description="Competition identifier")
    agent_id: UUID = Field(..., description="Agent identifier")
    challenge_id: str = Field(..., description="Challenge identifier")
    code: str = Field(..., description="Submitted code")
    status: SubmissionStatus = Field(..., description="Submission status")
    score: int = Field(0, description="Score achieved")
    tests_passed: int = Field(0, description="Number of tests passed")
    total_tests: int = Field(0, description="Total number of tests")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if any")
    attempts: int = Field(0, description="Number of attempts made")
    submitted_at: datetime = Field(default_factory=datetime.utcnow, description="Submission timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "competition_id": "550e8400-e29b-41d4-a716-446655440000",
                "agent_id": "550e8400-e29b-41d4-a716-446655440001",
                "challenge_id": "challenge-001",
                "code": "def solution(nums, target):\n    ...",
                "status": "passed",
                "score": 100,
                "tests_passed": 5,
                "total_tests": 5
            }
        }


class CompetitionResponse(BaseModel):
    """Competition response"""
    id: UUID = Field(default_factory=uuid4, description="Competition unique identifier")
    challenge_id: str = Field(..., description="Challenge identifier")
    agent_ids: List[UUID] = Field(..., description="List of competing agent IDs")
    status: CompetitionStatus = Field(..., description="Competition status")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    timeout_seconds: int = Field(300, description="Timeout in seconds per agent")

    class Config:
        json_schema_extra = {
            "example": {
                "challenge_id": "challenge-001",
                "agent_ids": [
                    "550e8400-e29b-41d4-a716-446655440001",
                    "550e8400-e29b-41d4-a716-446655440002"
                ],
                "status": "pending",
                "timeout_seconds": 300
            }
        }


class CompetitionResults(BaseModel):
    """Competition results"""
    competition_id: UUID = Field(..., description="Competition identifier")
    challenge: ChallengeResponse = Field(..., description="Challenge details")
    submissions: List[SubmissionResponse] = Field(..., description="All submissions")
    winner: Optional[UUID] = Field(None, description="Winning agent ID")
    leaderboard: List[Dict[str, Any]] = Field(default_factory=list, description="Ranked results")
    started_at: datetime = Field(..., description="Start timestamp")
    completed_at: datetime = Field(..., description="Completion timestamp")
    total_duration: float = Field(..., description="Total duration in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "competition_id": "550e8400-e29b-41d4-a716-446655440000",
                "winner": "550e8400-e29b-41d4-a716-446655440001",
                "total_duration": 45.2
            }
        }
