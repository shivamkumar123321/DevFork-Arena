# AI Agent System

Complete AI agent system for solving coding challenges autonomously using LangChain-powered agents with Anthropic Claude and OpenAI models.

## Overview

The AI Agent System enables autonomous solving of coding challenges through:

- **Abstract Base Framework**: Extensible base class for all AI agents
- **Multi-Model Support**: GPT (OpenAI) **[DEFAULT]** and Claude (Anthropic) implementations
- **LangChain Integration**: Leverages LangChain for robust LLM interactions
- **Iterative Problem Solving**: Automatic error analysis and solution refinement
- **Safe Code Execution**: Sandboxed environment for testing solutions

**Default Agent**: OpenAI GPT-4 Turbo is the default agent for maximum compatibility and performance.

## Architecture

```
agents/
├── base_agent.py          # Abstract base class defining agent interface
├── claude_agent.py        # Claude/Anthropic implementation
├── openai_agent.py        # OpenAI/GPT implementation
├── agent_factory.py       # Factory pattern for agent creation
├── code_executor.py       # Safe code execution and testing
└── __init__.py           # Module exports
```

## Core Components

### 1. BaseAgent (Abstract Class)

The foundation for all AI agents, defining:

```python
class BaseAgent(ABC):
    async def solve_challenge(challenge: ChallengeResponse) -> str
    async def analyze_and_iterate(challenge, previous_code, error_message) -> str
    async def format_challenge_prompt(challenge: ChallengeResponse) -> str

    @abstractmethod
    async def _generate_code(prompt: str) -> str

    @abstractmethod
    def _initialize_llm()
```

**Key Features:**
- Configuration management (temperature, max_tokens, system prompts)
- Challenge understanding and prompt formatting
- Iterative solution refinement
- Performance tracking and metrics

### 2. OpenAIAgent (DEFAULT)

OpenAI GPT-powered agent implementation - **the default agent**.

```python
from agents import create_default_agent  # Uses OpenAI by default

# Create default agent (OpenAI GPT-4 Turbo)
agent = create_default_agent(
    temperature=0.7,
    max_tokens=4096,
    max_iterations=3
)

# Or explicitly create OpenAI agent
from agents import create_openai_agent
agent = create_openai_agent(
    model_name="gpt-4-turbo-preview",
    temperature=0.7,
    max_tokens=4096,
    max_iterations=3
)

# Solve a challenge
solution = await agent.solve_challenge(challenge)
```

**Supported Models:**
- `gpt-4-turbo-preview` (latest GPT-4 Turbo) **[DEFAULT]**
- `gpt-4` (standard GPT-4)
- `gpt-4-32k` (extended context)
- `gpt-3.5-turbo` (faster, economical)

### 3. ClaudeAgent

Anthropic Claude-powered agent implementation.

```python
from agents import create_claude_agent

# Create agent
agent = create_claude_agent(
    model_name="claude-3-5-sonnet-20241022",
    temperature=0.7,
    max_tokens=4096,
    max_iterations=3
)

# Solve a challenge
solution = await agent.solve_challenge(challenge)
```

**Supported Models:**
- `claude-3-5-sonnet-20241022` (latest, most capable)
- `claude-3-opus-20240229` (powerful, slower)
- `claude-3-sonnet-20240229` (balanced)
- `claude-3-haiku-20240307` (fast, economical)

### 4. AgentFactory

Factory pattern for creating agents dynamically.

```python
from agents import AgentFactory, create_default_agent

# Create default agent (OpenAI)
default_agent = create_default_agent(temperature=0.5)

# Create by provider name
openai_agent = AgentFactory.create_agent("openai", temperature=0.5)  # Default
claude_agent = AgentFactory.create_agent("claude", temperature=0.5)

# List supported providers
providers = AgentFactory.list_supported_providers()
# ['anthropic', 'claude', 'openai', 'gpt']
```

### 5. CodeExecutor

Safe execution environment for testing code solutions.

```python
from agents import CodeExecutor

executor = CodeExecutor(timeout=5)

# Run test cases
result = executor.run_test_cases(
    code=solution_code,
    test_cases=challenge.test_cases
)

# Check syntax
is_valid, error = executor.validate_syntax(code)
```

### 5.1. MockCodeExecutor (NEW)

Mock executor for testing without actual code execution - simulates results with configurable randomness.

```python
from agents import MockCodeExecutor, mock_executor

# Create mock executor with 75% success rate
mock_exec = MockCodeExecutor(
    success_rate=0.75,
    random_seed=42  # For reproducible results
)

# Simulate test execution
result = mock_exec.run_test_cases(
    code=solution_code,
    test_cases=challenge.test_cases
)

# Adjust success rate dynamically
mock_exec.set_success_rate(0.9)

# Use global instance
result = mock_executor.run_test_cases(code, tests)
```

**Use Cases:**
- **Development**: Test agent logic without execution overhead
- **Testing**: Reproducible results with random seed
- **Prototyping**: Work without Docker sandboxing
- **Performance**: Fast simulations for benchmarking

**Features:**
- Configurable success rate (0.0 to 1.0)
- Random seed for reproducibility
- Realistic error simulation (IndexError, TypeError, etc.)
- Syntax validation (actually works)
- Simulated execution times

### 6. AgentManager (NEW)

Orchestrates competitions between multiple agents, manages submissions, and handles database persistence.

```python
from agents import AgentManager
from uuid import uuid4

# Create manager
manager = AgentManager(database=db)

# Run a competition
competition_id = uuid4()
results = await manager.run_competition(
    competition_id=competition_id,
    challenge=challenge,
    agent_ids=[agent1_id, agent2_id, agent3_id],
    timeout_per_agent=300
)

# View results
print(f"Winner: {results.winner}")
for entry in results.leaderboard:
    print(f"#{entry['rank']}: Score {entry['score']}")
```

**Key Features:**
- **Concurrent Execution**: Runs multiple agents in parallel
- **Database Integration**: Persists agents, competitions, and submissions
- **Timeout Management**: Handles agent timeouts gracefully
- **Result Tracking**: Maintains leaderboards and rankings
- **Resource Management**: Automatic cleanup and caching

### 7. PromptTemplates (NEW)

Specialized prompt templates for enhanced agent performance.

```python
from agents import PromptBuilder, format_challenge_prompt

# Build challenge prompt
prompt = PromptBuilder.build_challenge_prompt(
    title="Two Sum",
    difficulty="easy",
    description="Find two numbers that sum to target",
    test_cases=[
        {"input": "[2,7,11,15], 9", "expected_output": "[0,1]"}
    ],
    constraints="2 <= nums.length <= 10^4"
)

# Build iteration prompt after failure
iteration_prompt = PromptBuilder.build_iteration_prompt(
    title="Two Sum",
    previous_code=failed_code,
    error_message="IndexError: list index out of range",
    failed_tests=[
        {"input": "[3,3], 6", "expected": "[0,1]", "actual": "Error"}
    ]
)

# Quick prompt formatting
prompt = format_challenge_prompt(title="...", description="...")
```

**Available Templates:**
- **Challenge Solving**: Initial solution generation
- **Iteration**: Failed attempt improvement
- **Detailed Analysis**: Complex debugging
- **Optimization**: Performance improvement
- **Error Recovery**: Syntax/runtime error fixes

## Usage Examples

### Basic Usage

```python
import asyncio
from models import ChallengeResponse, TestCase, DifficultyLevel
from agents import create_default_agent  # Creates OpenAI agent by default

async def solve_challenge():
    # Create a challenge
    challenge = ChallengeResponse(
        id="challenge-001",
        title="Two Sum",
        description="Given an array and target, return indices that sum to target",
        difficulty=DifficultyLevel.EASY,
        test_cases=[
            TestCase(input="[2,7,11,15], 9", expected_output="[0,1]"),
            TestCase(input="[3,2,4], 6", expected_output="[1,2]"),
        ],
        tags=["array", "hash-table"]
    )

    # Create default agent (OpenAI GPT-4 Turbo)
    agent = create_default_agent()

    # Solve
    solution = await agent.solve_challenge(challenge)

    # Get performance metrics
    performance = agent.get_performance_summary()
    print(f"Solved in {performance['total_attempts']} attempts")
    print(f"Solution:\n{solution}")

asyncio.run(solve_challenge())
```

### Custom Configuration

```python
from models import AgentConfig
from agents import OpenAIAgent

# Custom configuration for OpenAI (default provider)
config = AgentConfig(
    name="Custom GPT-4 Solver",
    model_provider="openai",
    model_name="gpt-4-turbo-preview",
    temperature=0.5,
    max_tokens=8192,
    max_iterations=5,
    system_prompt="You are an expert competitive programmer..."
)

agent = OpenAIAgent(config)
```

### Agent Comparison

```python
async def compare_agents():
    challenge = get_challenge()

    # Create multiple agents (OpenAI first as default)
    agents = [
        create_openai_agent(name="GPT-4 Turbo (Default)"),
        create_claude_agent(name="Claude Sonnet"),
    ]

    # Compare performance
    results = {}
    for agent in agents:
        solution = await agent.solve_challenge(challenge)
        results[agent.config.name] = agent.get_performance_summary()

    # Analyze results
    for name, perf in results.items():
        print(f"{name}: {perf['total_attempts']} attempts, "
              f"Success: {perf['success']}")
```

### Using the Factory

```python
from agents import AgentFactory, create_default_agent

# Use default agent (OpenAI)
agent = create_default_agent()

# Dynamic agent creation
def create_agent_by_preference(preference):
    if preference == "fast":
        return AgentFactory.create_agent("openai",
            model_name="gpt-3.5-turbo")
    elif preference == "powerful":
        return AgentFactory.create_agent("openai",
            model_name="gpt-4")
    else:
        return create_default_agent()  # OpenAI GPT-4 Turbo

agent = create_agent_by_preference("powerful")
```

### Running Competitions

```python
import asyncio
from uuid import uuid4
from agents import AgentManager
from models import AgentRecord, ChallengeResponse

async def run_agent_competition():
    # Create manager
    manager = AgentManager(database=db)

    # Define competition
    competition_id = uuid4()
    challenge = get_challenge()  # Your challenge
    agent_ids = [agent1_id, agent2_id, agent3_id]

    # Run competition
    results = await manager.run_competition(
        competition_id=competition_id,
        challenge=challenge,
        agent_ids=agent_ids,
        timeout_per_agent=300  # 5 minutes per agent
    )

    # Display results
    print(f"Competition Duration: {results.total_duration:.2f}s")
    print(f"Winner: {results.winner}")

    print("\nLeaderboard:")
    for entry in results.leaderboard:
        print(
            f"#{entry['rank']}: Agent {entry['agent_id']} - "
            f"Score: {entry['score']}, "
            f"Status: {entry['status']}, "
            f"Time: {entry['execution_time']:.2f}s"
        )

    # Access individual submissions
    for submission in results.submissions:
        if submission.status.value == "passed":
            print(f"\nAgent {submission.agent_id} solution:")
            print(submission.code)

asyncio.run(run_agent_competition())
```

### Database Integration

```python
from agents import AgentManager
from database import db

# Create manager with database
manager = AgentManager(database=db)

# Load agent from database
agent_id = uuid4()
agent = await manager.load_agent_from_db(agent_id)

# Execute with automatic submission tracking
submission = await manager.execute_agent(
    agent_id=agent_id,
    challenge_id="challenge-001",
    competition_id=competition_id,
    challenge=challenge,
    timeout_seconds=300
)

# Submission automatically saved to database
print(f"Submission ID: {submission.id}")
print(f"Status: {submission.status.value}")
print(f"Score: {submission.score}")
```

## Configuration

### Environment Variables

Required environment variables in `.env`:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
TIGERDATA_CONNECTION_STRING=postgresql://user:pass@host:port/database
```

### Database Schema

The system uses TigerData Postgres with the following tables:

- **agents**: Store agent configurations
- **challenges**: Challenge definitions and test cases
- **competitions**: Competition records
- **competition_agents**: Many-to-many relationship for participants
- **submissions**: Code submissions and results
- **agent_stats**: Performance statistics

Initialize the database with:

```bash
psql -h your_host -U your_user -d your_database -f backend/schema.sql
```

Key views:
- `agent_leaderboard`: Ranked agents by total score
- `recent_competitions`: Latest competition results

### Agent Configuration Options

```python
AgentConfig(
    name: str,                    # Agent display name
    model_provider: str,          # "anthropic" or "openai"
    model_name: str,              # Specific model identifier
    temperature: float,           # 0.0-2.0, controls randomness
    max_tokens: int,              # Maximum tokens to generate
    max_iterations: int,          # Max solution attempts (1-10)
    system_prompt: Optional[str]  # Custom system prompt
)
```

## How It Works

### 1. Challenge Understanding

The agent receives a `ChallengeResponse` containing:
- Problem description
- Test cases
- Constraints
- Difficulty level
- Tags/categories

### 2. Prompt Formatting

The `format_challenge_prompt` method converts the challenge into a clear, structured prompt for the LLM.

### 3. Code Generation

The agent generates an initial solution using the LLM with the formatted prompt.

### 4. Testing & Validation

The generated code is tested against the provided test cases using the `CodeExecutor`.

### 5. Iterative Refinement

If tests fail:
1. Analyze the error/failure
2. Create an iteration prompt with:
   - Previous code
   - Error messages
   - Test failure details
3. Generate improved solution
4. Repeat until success or max iterations

### 6. Solution Return

Once all tests pass, the final solution is returned with performance metrics.

## Testing

### Agent System Demo

Test individual agents and basic functionality:

```bash
cd backend
python demo/agent_demo.py
```

The demo provides:
1. OpenAI Agent Demo (DEFAULT)
2. Claude Agent Demo
3. Agent Comparison
4. Agent Factory Demo

### Competition Demo

Test the AgentManager and competition orchestration:

```bash
cd backend
python demo/competition_demo.py
```

The competition demo showcases:
1. Basic Competition (Multiple Agents)
2. Single Agent Execution
3. Competition with Timeout Handling
4. Manager Statistics & Monitoring

## Performance Metrics

Each agent tracks:
- Total attempts
- Success/failure status
- Tests passed/failed
- Execution time
- Generated solutions

Access via `agent.get_performance_summary()`.

## Error Handling

The system handles:
- **Syntax Errors**: Detected before execution
- **Runtime Errors**: Caught and analyzed for iteration
- **Timeout Errors**: Configurable execution timeout
- **API Errors**: LLM API failures with clear messages
- **Test Failures**: Detailed failure information for refinement

## Best Practices

1. **Choose Appropriate Models**
   - Use GPT-4 Turbo (default) for most challenges
   - Use GPT-4 or Claude Sonnet for complex challenges
   - Use GPT-3.5 Turbo or Claude Haiku for simple/fast solutions

2. **Configure Temperature**
   - Lower (0.3-0.5) for deterministic solutions
   - Higher (0.7-1.0) for creative approaches

3. **Set Reasonable Iterations**
   - 3-5 iterations for most challenges
   - More iterations for complex problems

4. **Provide Clear Test Cases**
   - Include edge cases
   - Show expected input/output format
   - Add hidden test cases for validation

5. **Monitor Performance**
   - Track success rates
   - Analyze failure patterns
   - Optimize based on metrics

## Extending the System

### Adding a New Agent

1. Extend `BaseAgent`
2. Implement `_initialize_llm()`
3. Implement `_generate_code()`
4. Add to `AgentFactory`

Example:

```python
from base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def _initialize_llm(self):
        # Initialize your LLM
        pass

    async def _generate_code(self, prompt: str) -> str:
        # Generate code with your LLM
        pass
```

### Custom Code Executor

Extend `CodeExecutor` for custom testing logic:

```python
from agents import CodeExecutor

class CustomExecutor(CodeExecutor):
    async def _run_single_test(self, code, function_name, test_case, test_number):
        # Custom test execution logic
        pass
```

## Limitations

- Code execution is sandboxed but not fully isolated
- Limited to Python code generation
- Depends on LLM availability and rate limits
- Test execution has timeout constraints
- May require multiple iterations for complex problems

## Security Considerations

- All code is executed in a restricted namespace
- Import statements are limited
- File system access is restricted
- Network access is not available
- Timeout protection prevents infinite loops

## Future Enhancements

- [ ] Multi-language support (JavaScript, Java, C++, etc.)
- [ ] Docker-based sandboxing for complete isolation
- [ ] Parallel test execution
- [ ] Solution caching and learning
- [ ] Performance optimization based on historical data
- [ ] Integration with live coding platforms
- [ ] Real-time collaboration features
- [ ] Advanced metrics and analytics

## Support

For issues or questions:
- Check the demo script for examples
- Review the docstrings in each module
- Ensure API keys are correctly configured
- Check logs for detailed error information

## License

MIT License - See LICENSE file for details
