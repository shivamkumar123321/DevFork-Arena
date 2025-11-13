# Configuration Guide

Complete guide for configuring DevFork Arena.

## Overview

DevFork Arena uses a centralized configuration system built on Pydantic for type-safe settings management. All configuration can be set via environment variables or use sensible defaults.

## Quick Start

### 1. Copy Environment File

```bash
cp backend/.env.example backend/.env
```

### 2. Configure API Keys (Required)

```bash
# Edit .env file
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 3. Verify Configuration

```bash
cd backend
python demo_config.py
```

---

## Configuration Sections

### 1. Agent Configuration

Controls agent behavior and execution.

```bash
# Default agent parameters
AGENT_DEFAULT_TEMPERATURE=0.7          # LLM randomness (0.0-2.0)
AGENT_DEFAULT_MAX_TOKENS=4096          # Maximum tokens to generate
AGENT_DEFAULT_MAX_ITERATIONS=3         # Max solution attempts

# Timeouts (seconds)
AGENT_TIMEOUT_SECONDS=300              # 5 minutes per agent
CODE_EXECUTION_TIMEOUT=5               # 5 seconds per code execution
COMPETITION_TIMEOUT_SECONDS=1800       # 30 minutes per competition

# Retries
MAX_RETRY_ATTEMPTS=3                   # Retry failed operations
RETRY_DELAY_SECONDS=2.0                # Delay between retries

# Concurrency
MAX_CONCURRENT_AGENTS=10               # Max parallel agents
```

**Usage in Code:**
```python
from config import settings

agent = create_default_agent(
    temperature=settings.agent.default_temperature,
    max_tokens=settings.agent.default_max_tokens,
    max_iterations=settings.agent.default_max_iterations
)
```

---

### 2. Model Configuration

LLM model selection and defaults.

```bash
# Default provider
DEFAULT_PROVIDER=openai                # openai or anthropic

# OpenAI models
OPENAI_DEFAULT_MODEL=gpt-4-turbo-preview
OPENAI_FAST_MODEL=gpt-3.5-turbo
OPENAI_POWERFUL_MODEL=gpt-4

# Anthropic models
ANTHROPIC_DEFAULT_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_FAST_MODEL=claude-3-haiku-20240307
ANTHROPIC_POWERFUL_MODEL=claude-3-opus-20240229
```

**Model Selection Strategy:**
- **Fast models**: Simple problems, quick responses
- **Default models**: Balanced performance and quality
- **Powerful models**: Complex problems, highest quality

**Usage in Code:**
```python
from config import settings

# Select model based on difficulty
if difficulty == "easy":
    model = settings.model.openai_fast_model
elif difficulty == "hard":
    model = settings.model.openai_powerful_model
else:
    model = settings.model.openai_default_model
```

---

### 3. API Server Configuration

FastAPI server settings.

```bash
# Server settings
API_HOST=0.0.0.0                       # Listen on all interfaces
API_PORT=8000                          # Server port
API_RELOAD=true                        # Auto-reload on code changes

# CORS settings (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100                # Max requests per window
RATE_LIMIT_WINDOW_SECONDS=60           # Time window in seconds

# Request limits
MAX_REQUEST_SIZE_MB=10                 # Maximum request body size
```

**Usage in Code:**
```python
from config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=settings.api.cors_allow_credentials,
    allow_methods=settings.api.cors_allow_methods,
    allow_headers=settings.api.cors_allow_headers
)
```

---

### 4. Database Configuration

TigerData Postgres connection settings.

```bash
# Connection
TIGERDATA_CONNECTION_STRING=postgresql://user:pass@host:port/db

# Connection pool
DB_POOL_SIZE=10                        # Connection pool size
DB_POOL_TIMEOUT=30                     # Pool timeout (seconds)

# Query settings
DB_QUERY_TIMEOUT=30                    # Query timeout (seconds)

# Retry settings
DB_MAX_RETRIES=3                       # Max connection retries
DB_RETRY_DELAY=1.0                     # Retry delay (seconds)
```

**Usage in Code:**
```python
from config import settings
import asyncpg

pool = await asyncpg.create_pool(
    settings.database.connection_string,
    min_size=1,
    max_size=settings.database.pool_size,
    timeout=settings.database.pool_timeout
)
```

---

### 5. Competition Configuration

Competition management settings.

```bash
# Competition limits
MIN_AGENTS_PER_COMPETITION=2           # Minimum agents required
MAX_AGENTS_PER_COMPETITION=50          # Maximum agents allowed

# Timeouts
DEFAULT_COMPETITION_TIMEOUT=300        # 5 minutes per agent

# Status polling
STATUS_POLL_INTERVAL=5                 # Recommended poll interval

# Scoring weights
SCORE_BASE=1000                        # Base score for perfect solution
SCORE_TIME_WEIGHT=0.3                  # Weight of execution time
SCORE_ATTEMPTS_WEIGHT=0.2              # Weight of attempt count
```

**Scoring Formula:**
```
score = SCORE_BASE
        × (tests_passed / total_tests)
        × (1 - TIME_WEIGHT × normalized_time)
        × (1 - ATTEMPTS_WEIGHT × normalized_attempts)
        × difficulty_multiplier
```

**Usage in Code:**
```python
from config import settings

def validate_competition(agent_ids):
    min_agents = settings.competition.min_agents_per_competition
    max_agents = settings.competition.max_agents_per_competition

    if not (min_agents <= len(agent_ids) <= max_agents):
        raise ValueError(
            f"Agent count must be between {min_agents} and {max_agents}"
        )
```

---

### 6. Logging Configuration

Application logging settings.

```bash
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_FILE_ENABLED=false                 # Enable file logging
LOG_FILE_PATH=logs/devfork_arena.log   # Log file path
```

**Usage in Code:**
```python
from config import settings
import logging

logging.basicConfig(
    level=settings.logging.level,
    format=settings.logging.format
)

logger = logging.getLogger(__name__)
```

---

### 7. Security Configuration

API keys and authentication.

```bash
# API Keys (REQUIRED)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Authentication (future feature)
AUTH_ENABLED=false
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Validation:**
```python
from config import settings

# Check if API keys are configured
is_valid, missing = settings.validate_api_keys()
if not is_valid:
    print(f"Missing: {', '.join(missing)}")
```

---

## Environment-Specific Configuration

### Development

```bash
ENVIRONMENT=development
DEBUG=true
API_RELOAD=true
LOG_LEVEL=DEBUG
```

### Production

```bash
ENVIRONMENT=production
DEBUG=false
API_RELOAD=false
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
```

### Staging

```bash
ENVIRONMENT=staging
DEBUG=false
API_RELOAD=false
LOG_LEVEL=INFO
```

---

## Usage Examples

### Basic Usage

```python
from config import settings

# Access configuration
print(f"API Port: {settings.api.port}")
print(f"Agent timeout: {settings.agent.agent_timeout_seconds}s")
print(f"Default model: {settings.model.openai_default_model}")
```

### Full Configuration Access

```python
from config import get_settings

settings = get_settings()

# Agent config
agent_config = settings.agent
print(f"Temperature: {agent_config.default_temperature}")
print(f"Max tokens: {agent_config.default_max_tokens}")

# Model config
model_config = settings.model
print(f"Provider: {model_config.default_provider}")

# API config
api_config = settings.api
print(f"Port: {api_config.port}")
```

### Validation

```python
from config import validate_configuration

is_valid, errors = validate_configuration()

if not is_valid:
    print("Configuration errors:")
    for error in errors:
        print(f"  - {error}")
    exit(1)
```

### Print Configuration

```python
from config import print_settings

# Print all settings (hides sensitive data)
print_settings(hide_sensitive=True)
```

### Reload Configuration

```python
from config import reload_settings

# After modifying .env file
new_settings = reload_settings()
```

---

## Integration with Existing Code

### Updating main.py

```python
from config import settings, validate_configuration

# Validate on startup
is_valid, errors = validate_configuration()
if not is_valid:
    for error in errors:
        print(f"Configuration error: {error}")

app = FastAPI(
    title="DevFork Arena API",
    debug=settings.debug
)

# Use config for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=settings.api.cors_allow_credentials
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload
    )
```

### Updating Agent Creation

```python
from config import settings

def create_configured_agent(provider: str = None):
    """Create agent with configuration defaults."""
    provider = provider or settings.model.default_provider

    if provider == "openai":
        model = settings.model.openai_default_model
    else:
        model = settings.model.anthropic_default_model

    return create_agent(
        provider=provider,
        model_name=model,
        temperature=settings.agent.default_temperature,
        max_tokens=settings.agent.default_max_tokens,
        max_iterations=settings.agent.default_max_iterations
    )
```

### Updating Competition Service

```python
from config import settings

class CompetitionService:
    def __init__(self):
        self.timeout = settings.competition.default_competition_timeout
        self.min_agents = settings.competition.min_agents_per_competition
        self.max_agents = settings.competition.max_agents_per_competition

    async def run_competition(self, competition_id, agent_ids):
        # Validate agent count
        if not (self.min_agents <= len(agent_ids) <= self.max_agents):
            raise ValueError(
                f"Agent count must be between {self.min_agents} and {self.max_agents}"
            )

        # Use configured timeout
        await self.execute_with_timeout(
            competition_id,
            timeout=self.timeout
        )
```

---

## Configuration Testing

### Test Script

```bash
cd backend
python demo_config.py
```

### Verify API Keys

```python
from config import settings

is_valid, missing = settings.validate_api_keys()
if is_valid:
    print("✓ All API keys configured")
else:
    print(f"✗ Missing: {', '.join(missing)}")
```

### Verify Database

```python
from config import settings

if settings.validate_database():
    print("✓ Database configured")
else:
    print("✗ Database not configured")
```

---

## Best Practices

### 1. Never Hardcode Values

❌ **Bad:**
```python
timeout = 300  # Hardcoded
temperature = 0.7  # Hardcoded
```

✅ **Good:**
```python
from config import settings

timeout = settings.agent.agent_timeout_seconds
temperature = settings.agent.default_temperature
```

### 2. Validate on Startup

```python
from config import validate_configuration

# In main.py or app startup
is_valid, errors = validate_configuration()
if not is_valid:
    for error in errors:
        logger.error(f"Config error: {error}")
    raise RuntimeError("Invalid configuration")
```

### 3. Use Type-Safe Access

```python
from config import settings

# Pydantic ensures types are correct
port: int = settings.api.port  # Always an int
temperature: float = settings.agent.default_temperature  # Always a float
```

### 4. Environment-Specific Settings

```python
from config import settings

if settings.environment == "production":
    # Production-specific logic
    enable_monitoring()
    disable_debug()
elif settings.environment == "development":
    # Development-specific logic
    enable_debug()
```

### 5. Document Custom Settings

When adding new configuration:
1. Add to appropriate config class in `config.py`
2. Add to `.env.example` with description
3. Update this documentation
4. Add validation if needed

---

## Troubleshooting

### Missing API Keys

**Error:**
```
Missing API keys: ANTHROPIC_API_KEY, OPENAI_API_KEY
```

**Solution:**
```bash
# Add to .env file
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### Invalid Configuration

**Error:**
```
Invalid log level. Must be one of: ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
```

**Solution:**
```bash
# Fix in .env
LOG_LEVEL=INFO
```

### Database Not Configured

**Warning:**
```
Database not configured (TIGERDATA_CONNECTION_STRING not set)
```

**Solution:**
```bash
# Add to .env
TIGERDATA_CONNECTION_STRING=postgresql://user:pass@host:port/db
```

---

## Configuration Reference

Complete list of all configuration variables with defaults:

| Variable | Default | Description |
|----------|---------|-------------|
| **Environment** | | |
| `ENVIRONMENT` | `development` | Environment name |
| `DEBUG` | `true` | Debug mode |
| **Agent** | | |
| `AGENT_DEFAULT_TEMPERATURE` | `0.7` | LLM temperature |
| `AGENT_DEFAULT_MAX_TOKENS` | `4096` | Max tokens |
| `AGENT_DEFAULT_MAX_ITERATIONS` | `3` | Max attempts |
| `AGENT_TIMEOUT_SECONDS` | `300` | Agent timeout |
| `CODE_EXECUTION_TIMEOUT` | `5` | Code timeout |
| `MAX_RETRY_ATTEMPTS` | `3` | Retry attempts |
| `MAX_CONCURRENT_AGENTS` | `10` | Max parallel |
| **Model** | | |
| `DEFAULT_PROVIDER` | `openai` | Default provider |
| `OPENAI_DEFAULT_MODEL` | `gpt-4-turbo-preview` | OpenAI model |
| `ANTHROPIC_DEFAULT_MODEL` | `claude-3-5-sonnet...` | Claude model |
| **API** | | |
| `API_HOST` | `0.0.0.0` | Server host |
| `API_PORT` | `8000` | Server port |
| `RATE_LIMIT_REQUESTS` | `100` | Rate limit |
| **Competition** | | |
| `MIN_AGENTS_PER_COMPETITION` | `2` | Min agents |
| `MAX_AGENTS_PER_COMPETITION` | `50` | Max agents |
| `SCORE_BASE` | `1000` | Base score |

See `.env.example` for complete list.

---

## Additional Resources

- **Demo Script**: `backend/demo_config.py`
- **Environment Template**: `backend/.env.example`
- **Configuration Module**: `backend/config.py`
- **API Documentation**: `backend/API_DOCUMENTATION.md`
