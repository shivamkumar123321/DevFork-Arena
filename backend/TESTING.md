# Testing & Validation Guide

Comprehensive testing documentation for DevFork Arena.

## Overview

The DevFork Arena testing system includes:
1. **Test Agents**: Agents with predictable behavior for testing
2. **Test Challenges**: Simple coding challenges with known solutions
3. **Validation Suite**: Comprehensive tests verifying all system components
4. **Integration Tests**: End-to-end testing of the complete flow

---

## Test Agents

Special agent implementations for testing without LLM API calls.

### Available Test Agents

#### 1. AlwaysPassAgent
Returns hardcoded correct solutions for common challenges.

```python
from agents import AlwaysPassAgent

agent = AlwaysPassAgent(name="TestAgent", solution_delay=0.1)
code = await agent.solve_challenge(challenge)
```

**Supported Challenges:**
- FizzBuzz
- Two Sum
- Reverse String
- Palindrome
- Factorial
- Fibonacci

**Use Cases:**
- Testing competition flow with guaranteed success
- Verifying scoring and ranking systems
- Performance benchmarking

---

#### 2. AlwaysFailAgent
Returns syntactically valid but logically incorrect solutions.

```python
from agents import AlwaysFailAgent

agent = AlwaysFailAgent(name="FailAgent")
code = await agent.solve_challenge(challenge)
# Code will be valid Python but fail all tests
```

**Use Cases:**
- Testing error handling
- Verifying failure tracking
- Testing leaderboard with failed submissions

---

#### 3. TimeoutAgent
Simulates agents that take too long to respond.

```python
from agents import TimeoutAgent

agent = TimeoutAgent(name="SlowAgent", timeout_duration=10)
# Will sleep for 10 seconds before returning
```

**Use Cases:**
- Testing timeout handling
- Verifying competition doesn't hang on slow agents
- Testing concurrent execution with timeouts

---

#### 4. RandomAgent
Randomly succeeds or fails based on configured success rate.

```python
from agents import RandomAgent

agent = RandomAgent(name="UnpredictableAgent", success_rate=0.7)
# 70% chance of success
```

**Use Cases:**
- Stress testing
- Simulating realistic agent behavior
- Testing statistical analysis

---

#### 5. SlowAgent
Returns correct solutions but takes longer to respond.

```python
from agents import SlowAgent

agent = SlowAgent(name="SlowButCorrect", delay=2.0)
# Takes 2 seconds to think before responding
```

**Use Cases:**
- Testing performance-based ranking
- Verifying faster agents rank higher
- Testing concurrent execution performance

---

## Test Challenges

Simple challenges for validation testing.

### Available Challenges

```python
from test_challenges import (
    get_fizzbuzz_challenge,
    get_two_sum_challenge,
    get_reverse_string_challenge,
    get_palindrome_challenge,
    get_factorial_challenge,
    get_fibonacci_challenge,
    get_all_test_challenges
)

# Get a specific challenge
challenge = get_fizzbuzz_challenge()

# Get all challenges
challenges = get_all_test_challenges()

# Get random challenge
from test_challenges import get_random_challenge
challenge = get_random_challenge()
```

### Challenge Details

| Challenge | Difficulty | Function | Description |
|-----------|-----------|----------|-------------|
| FizzBuzz | Easy | `fizzbuzz(n)` | Classic FizzBuzz sequence |
| Two Sum | Easy | `two_sum(nums, target)` | Find two numbers that sum to target |
| Reverse String | Easy | `reverse_string(s)` | Reverse a string |
| Palindrome | Easy | `is_palindrome(s)` | Check if palindrome |
| Factorial | Easy | `factorial(n)` | Calculate factorial |
| Fibonacci | Easy | `fibonacci(n)` | Calculate nth Fibonacci number |

All challenges include:
- Clear description
- Multiple test cases
- Expected outputs
- Constraints
- Tags

---

## Validation Test Suite

Comprehensive tests validating all system components.

### Running Tests

```bash
# Run all tests
cd backend
python test_validation.py

# Run specific test suite
python test_validation.py --suite basic
python test_validation.py --suite concurrency
python test_validation.py --suite orchestration
python test_validation.py --suite error

# Show success criteria
python test_validation.py --criteria
```

### Test Suites

#### Basic Agent Tests
- ✅ AlwaysPassAgent solves challenges
- ✅ AlwaysFailAgent fails correctly
- ✅ TimeoutAgent times out properly
- ✅ All test challenges can be solved

#### Concurrency Tests
- ✅ Multiple agents run sequentially
- ✅ Multiple agents run concurrently
- ✅ No race conditions or deadlocks

#### Orchestration Tests
- ✅ AgentManager orchestrates competitions
- ✅ CompetitionService end-to-end flow
- ✅ Performance-based ranking works

#### Error Handling Tests
- ✅ Graceful handling of invalid inputs
- ✅ Timeout handling
- ✅ API failure recovery

---

## Success Criteria Checklist

All items from the implementation checklist:

```
✅ Can create agent instances from database configs
✅ Agents can read and understand challenges
✅ Agents generate syntactically valid code
✅ Competition orchestration works end-to-end
✅ Multiple agents can run concurrently
✅ Submissions are created and tracked
✅ Winners are determined correctly
✅ Leaderboard updates automatically
✅ Error handling for API failures
✅ Timeout handling for slow agents
```

---

## Example Usage

### Basic Agent Test

```python
from agents import AlwaysPassAgent
from test_challenges import get_fizzbuzz_challenge

async def test_basic():
    agent = AlwaysPassAgent()
    challenge = get_fizzbuzz_challenge()

    code = await agent.solve_challenge(challenge)

    if agent.solution_attempts[0].test_result.passed:
        print("✅ Test passed!")
    else:
        print("❌ Test failed!")
```

### Competition Test

```python
from agents import AlwaysPassAgent, SlowAgent, AlwaysFailAgent
from agents import AgentManager
from test_challenges import get_two_sum_challenge
from uuid import uuid4

async def test_competition():
    manager = AgentManager()
    challenge = get_two_sum_challenge()

    # Create agents
    agent_ids = [uuid4() for _ in range(3)]
    manager.agent_cache[agent_ids[0]] = AlwaysPassAgent(name="Fast")
    manager.agent_cache[agent_ids[1]] = SlowAgent(name="Slow", delay=1.0)
    manager.agent_cache[agent_ids[2]] = AlwaysFailAgent(name="Fail")

    # Run competition
    results = await manager.run_competition(
        competition_id=uuid4(),
        challenge=challenge,
        agent_ids=agent_ids,
        timeout_per_agent=10
    )

    print(f"Winner: {results.winner}")
    for entry in results.leaderboard:
        print(f"#{entry['rank']}: {entry['agent_id']} - Score: {entry['score']}")
```

### Full System Test

```python
from services import create_competition_service
from agents import AlwaysPassAgent
from test_challenges import get_fizzbuzz_challenge
from uuid import uuid4

async def test_full_system():
    service = create_competition_service()
    challenge = get_fizzbuzz_challenge()

    # Create competition
    agent_ids = [uuid4(), uuid4()]
    competition = await service.create_competition(
        challenge_id=challenge.id,
        agent_ids=agent_ids,
        name="Test Competition"
    )

    # Register test agents
    service.agent_manager.agent_cache[agent_ids[0]] = AlwaysPassAgent(name="A1")
    service.agent_manager.agent_cache[agent_ids[1]] = AlwaysPassAgent(name="A2")

    # Run competition
    results = await service.run_competition(
        competition_id=competition.id,
        timeout_per_agent=10
    )

    print(f"Competition completed!")
    print(f"Winner: {results.winner}")
    print(f"Duration: {results.total_duration:.2f}s")
```

---

## Integration Testing

### Testing with API

```bash
# Terminal 1: Start server
cd backend
python main.py

# Terminal 2: Run API tests
python test_api.py --full
```

### Testing Competition Flow

```python
import requests

# Create competition
response = requests.post("http://localhost:8000/api/competitions/", json={
    "challenge_id": "test-fizzbuzz",
    "agent_ids": [str(uuid4()), str(uuid4())]
})
competition_id = response.json()["id"]

# Start competition
requests.post(f"http://localhost:8000/api/competitions/{competition_id}/start")

# Monitor status
while True:
    status = requests.get(
        f"http://localhost:8000/api/competitions/{competition_id}/status"
    ).json()

    if status["status"] == "completed":
        break

    time.sleep(2)

# Get results
results = requests.get(
    f"http://localhost:8000/api/competitions/{competition_id}/results"
).json()

print(f"Winner: {results['winner']}")
```

---

## Performance Testing

### Stress Test

Test with many concurrent agents:

```python
from agents import AlwaysPassAgent
from test_challenges import get_random_challenge
import asyncio

async def stress_test(num_agents=20):
    challenge = get_random_challenge()
    agents = [AlwaysPassAgent(name=f"Agent{i}") for i in range(num_agents)]

    start = datetime.now()

    tasks = [agent.solve_challenge(challenge) for agent in agents]
    results = await asyncio.gather(*tasks)

    duration = (datetime.now() - start).total_seconds()

    print(f"Completed {num_agents} agents in {duration:.2f}s")
    print(f"Average: {duration/num_agents:.2f}s per agent")
```

### Timeout Test

Verify timeout handling:

```python
from agents import TimeoutAgent

async def timeout_test():
    agent = TimeoutAgent(timeout_duration=10)
    challenge = get_fizzbuzz_challenge()

    try:
        await asyncio.wait_for(
            agent.solve_challenge(challenge),
            timeout=2.0
        )
        print("❌ Should have timed out")
    except asyncio.TimeoutError:
        print("✅ Timeout handled correctly")
```

---

## Continuous Integration

### CI Test Script

```bash
#!/bin/bash
# ci_test.sh

echo "Running DevFork Arena Test Suite..."

# Run validation tests
python backend/test_validation.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Tests failed!"
    exit 1
fi
```

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt

      - name: Run validation tests
        run: |
          python backend/test_validation.py
```

---

## Troubleshooting Tests

### Common Issues

#### Import Errors
```python
# Wrong
from test_agents import AlwaysPassAgent

# Correct
from agents import AlwaysPassAgent
```

#### Async Errors
```python
# Wrong
code = agent.solve_challenge(challenge)

# Correct
code = await agent.solve_challenge(challenge)
```

#### Timeout Issues
```python
# Increase timeout if needed
await asyncio.wait_for(
    agent.solve_challenge(challenge),
    timeout=30.0  # Increase from default
)
```

---

## Best Practices

### 1. Use Test Agents for CI/CD
Don't rely on LLM APIs in automated tests - use test agents instead.

### 2. Test All Scenarios
- Success cases (AlwaysPassAgent)
- Failure cases (AlwaysFailAgent)
- Timeouts (TimeoutAgent)
- Performance (SlowAgent)
- Unpredictability (RandomAgent)

### 3. Verify Error Handling
Always test error paths, not just happy paths.

### 4. Test Concurrency
Ensure system works with multiple simultaneous competitions.

### 5. Monitor Performance
Track execution times to detect regressions.

---

## Test Coverage

Target coverage areas:

- ✅ Agent creation and initialization
- ✅ Challenge understanding
- ✅ Code generation
- ✅ Code execution and testing
- ✅ Error handling and recovery
- ✅ Timeout handling
- ✅ Competition orchestration
- ✅ Concurrent execution
- ✅ Scoring and ranking
- ✅ Leaderboard updates
- ✅ API endpoints
- ✅ Database operations (when integrated)

---

## Additional Resources

- **Test Agents**: `backend/agents/test_agents.py`
- **Test Challenges**: `backend/test_challenges.py`
- **Validation Suite**: `backend/test_validation.py`
- **API Tests**: `backend/test_api.py`
- **Demo Scripts**: `backend/demo/*.py`

---

## Quick Reference

### Run All Tests
```bash
python backend/test_validation.py
```

### Run Specific Suite
```bash
python backend/test_validation.py --suite basic
```

### Create Test Agent
```python
from agents import create_test_agent

agent = create_test_agent("pass", name="MyAgent")
```

### Get Test Challenge
```python
from test_challenges import get_fizzbuzz_challenge

challenge = get_fizzbuzz_challenge()
```

### Run Competition
```python
from agents import AgentManager
from uuid import uuid4

manager = AgentManager()
results = await manager.run_competition(
    competition_id=uuid4(),
    challenge=challenge,
    agent_ids=agent_ids,
    timeout_per_agent=10
)
```

---

**Testing is complete and comprehensive!** 🎉

All success criteria from the implementation checklist are validated.
