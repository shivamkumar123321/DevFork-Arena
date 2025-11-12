"""
Configuration & Settings

Centralized configuration management for DevFork Arena.
Uses Pydantic for validation and environment variable loading.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AgentConfig(BaseModel):
    """Agent execution configuration."""

    # Default agent parameters
    default_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Default temperature for LLM generation"
    )
    default_max_tokens: int = Field(
        default=4096,
        ge=1,
        le=100000,
        description="Default maximum tokens to generate"
    )
    default_max_iterations: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Default maximum solution attempts"
    )

    # Timeouts
    agent_timeout_seconds: int = Field(
        default=300,
        ge=10,
        le=3600,
        description="Default timeout per agent execution (5 minutes)"
    )
    code_execution_timeout: int = Field(
        default=5,
        ge=1,
        le=60,
        description="Timeout for individual code execution (5 seconds)"
    )
    competition_timeout_seconds: int = Field(
        default=1800,
        ge=60,
        le=7200,
        description="Maximum competition duration (30 minutes)"
    )

    # Retries
    max_retry_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts for failed operations"
    )
    retry_delay_seconds: float = Field(
        default=2.0,
        ge=0.1,
        le=60.0,
        description="Delay between retry attempts"
    )

    # Concurrency
    max_concurrent_agents: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum agents that can run concurrently"
    )

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables."""
        return cls(
            default_temperature=float(os.getenv("AGENT_DEFAULT_TEMPERATURE", "0.7")),
            default_max_tokens=int(os.getenv("AGENT_DEFAULT_MAX_TOKENS", "4096")),
            default_max_iterations=int(os.getenv("AGENT_DEFAULT_MAX_ITERATIONS", "3")),
            agent_timeout_seconds=int(os.getenv("AGENT_TIMEOUT_SECONDS", "300")),
            code_execution_timeout=int(os.getenv("CODE_EXECUTION_TIMEOUT", "5")),
            competition_timeout_seconds=int(os.getenv("COMPETITION_TIMEOUT_SECONDS", "1800")),
            max_retry_attempts=int(os.getenv("MAX_RETRY_ATTEMPTS", "3")),
            retry_delay_seconds=float(os.getenv("RETRY_DELAY_SECONDS", "2.0")),
            max_concurrent_agents=int(os.getenv("MAX_CONCURRENT_AGENTS", "10"))
        )


class ModelConfig(BaseModel):
    """LLM model configuration."""

    # OpenAI models
    openai_default_model: str = Field(
        default="gpt-4-turbo-preview",
        description="Default OpenAI model"
    )
    openai_fast_model: str = Field(
        default="gpt-3.5-turbo",
        description="Fast/economical OpenAI model"
    )
    openai_powerful_model: str = Field(
        default="gpt-4",
        description="Most powerful OpenAI model"
    )

    # Anthropic models
    anthropic_default_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Default Anthropic Claude model"
    )
    anthropic_fast_model: str = Field(
        default="claude-3-haiku-20240307",
        description="Fast/economical Claude model"
    )
    anthropic_powerful_model: str = Field(
        default="claude-3-opus-20240229",
        description="Most powerful Claude model"
    )

    # Default provider
    default_provider: str = Field(
        default="openai",
        description="Default LLM provider (openai or anthropic)"
    )

    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Load configuration from environment variables."""
        return cls(
            openai_default_model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4-turbo-preview"),
            openai_fast_model=os.getenv("OPENAI_FAST_MODEL", "gpt-3.5-turbo"),
            openai_powerful_model=os.getenv("OPENAI_POWERFUL_MODEL", "gpt-4"),
            anthropic_default_model=os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-3-5-sonnet-20241022"),
            anthropic_fast_model=os.getenv("ANTHROPIC_FAST_MODEL", "claude-3-haiku-20240307"),
            anthropic_powerful_model=os.getenv("ANTHROPIC_POWERFUL_MODEL", "claude-3-opus-20240229"),
            default_provider=os.getenv("DEFAULT_PROVIDER", "openai")
        )


class APIConfig(BaseModel):
    """API server configuration."""

    # Server settings
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, ge=1, le=65535, description="API port")
    reload: bool = Field(default=True, description="Auto-reload on code changes")

    # CORS settings
    cors_origins: list = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: list = Field(default=["*"])
    cors_allow_headers: list = Field(default=["*"])

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(
        default=100,
        ge=1,
        description="Maximum requests per window"
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        ge=1,
        description="Rate limit time window (seconds)"
    )

    # Request limits
    max_request_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum request body size in MB"
    )

    @classmethod
    def from_env(cls) -> "APIConfig":
        """Load configuration from environment variables."""
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
        cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

        return cls(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            reload=os.getenv("API_RELOAD", "true").lower() == "true",
            cors_origins=cors_origins,
            rate_limit_enabled=os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
            rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
            rate_limit_window_seconds=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")),
            max_request_size_mb=int(os.getenv("MAX_REQUEST_SIZE_MB", "10"))
        )


class DatabaseConfig(BaseModel):
    """Database configuration."""

    # Connection settings
    connection_string: Optional[str] = Field(
        default=None,
        description="TigerData Postgres connection string"
    )
    pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Database connection pool size"
    )
    pool_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Connection pool timeout (seconds)"
    )

    # Query settings
    query_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Query execution timeout (seconds)"
    )

    # Retry settings
    max_connection_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum database connection retry attempts"
    )
    connection_retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Delay between connection retry attempts"
    )

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Load configuration from environment variables."""
        return cls(
            connection_string=os.getenv("TIGERDATA_CONNECTION_STRING"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            query_timeout=int(os.getenv("DB_QUERY_TIMEOUT", "30")),
            max_connection_retries=int(os.getenv("DB_MAX_RETRIES", "3")),
            connection_retry_delay=float(os.getenv("DB_RETRY_DELAY", "1.0"))
        )


class CompetitionConfig(BaseModel):
    """Competition management configuration."""

    # Competition limits
    min_agents_per_competition: int = Field(
        default=2,
        ge=1,
        description="Minimum agents required for a competition"
    )
    max_agents_per_competition: int = Field(
        default=50,
        ge=1,
        description="Maximum agents allowed in a competition"
    )

    # Timeouts
    default_competition_timeout: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Default timeout per agent in competition (5 minutes)"
    )

    # Status polling
    status_poll_interval_seconds: int = Field(
        default=5,
        ge=1,
        le=60,
        description="Recommended status polling interval"
    )

    # Scoring
    score_base: int = Field(
        default=1000,
        ge=100,
        description="Base score for perfect solution"
    )
    score_time_weight: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Weight of execution time in scoring"
    )
    score_attempts_weight: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Weight of attempt count in scoring"
    )

    @classmethod
    def from_env(cls) -> "CompetitionConfig":
        """Load configuration from environment variables."""
        return cls(
            min_agents_per_competition=int(os.getenv("MIN_AGENTS_PER_COMPETITION", "2")),
            max_agents_per_competition=int(os.getenv("MAX_AGENTS_PER_COMPETITION", "50")),
            default_competition_timeout=int(os.getenv("DEFAULT_COMPETITION_TIMEOUT", "300")),
            status_poll_interval_seconds=int(os.getenv("STATUS_POLL_INTERVAL", "5")),
            score_base=int(os.getenv("SCORE_BASE", "1000")),
            score_time_weight=float(os.getenv("SCORE_TIME_WEIGHT", "0.3")),
            score_attempts_weight=float(os.getenv("SCORE_ATTEMPTS_WEIGHT", "0.2"))
        )


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    file_enabled: bool = Field(
        default=False,
        description="Enable logging to file"
    )
    file_path: str = Field(
        default="logs/devfork_arena.log",
        description="Log file path"
    )

    @validator("level")
    def validate_level(cls, v):
        """Validate logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v.upper()

    @classmethod
    def from_env(cls) -> "LoggingConfig":
        """Load configuration from environment variables."""
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            file_enabled=os.getenv("LOG_FILE_ENABLED", "false").lower() == "true",
            file_path=os.getenv("LOG_FILE_PATH", "logs/devfork_arena.log")
        )


class SecurityConfig(BaseModel):
    """Security configuration."""

    # API keys
    anthropic_api_key: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)

    # Authentication (for future use)
    auth_enabled: bool = Field(default=False, description="Enable API authentication")
    jwt_secret_key: Optional[str] = Field(default=None)
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Load configuration from environment variables."""
        return cls(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            auth_enabled=os.getenv("AUTH_ENABLED", "false").lower() == "true",
            jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
            jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        )


class Settings(BaseModel):
    """Main application settings."""

    # Environment
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)"
    )
    debug: bool = Field(
        default=True,
        description="Debug mode"
    )

    # Configuration sections
    agent: AgentConfig = Field(default_factory=AgentConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    competition: CompetitionConfig = Field(default_factory=CompetitionConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    @classmethod
    def from_env(cls) -> "Settings":
        """Load all configuration from environment variables."""
        return cls(
            environment=os.getenv("ENVIRONMENT", "development"),
            debug=os.getenv("DEBUG", "true").lower() == "true",
            agent=AgentConfig.from_env(),
            model=ModelConfig.from_env(),
            api=APIConfig.from_env(),
            database=DatabaseConfig.from_env(),
            competition=CompetitionConfig.from_env(),
            logging=LoggingConfig.from_env(),
            security=SecurityConfig.from_env()
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "agent": self.agent.dict(),
            "model": self.model.dict(),
            "api": self.api.dict(),
            "database": self.database.dict(exclude={"connection_string"}),  # Hide sensitive
            "competition": self.competition.dict(),
            "logging": self.logging.dict(),
            "security": {
                "auth_enabled": self.security.auth_enabled,
                # Hide API keys
            }
        }

    def validate_api_keys(self) -> tuple[bool, list[str]]:
        """
        Validate that required API keys are configured.

        Returns:
            Tuple of (is_valid, missing_keys)
        """
        missing = []

        if not self.security.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")

        if not self.security.openai_api_key:
            missing.append("OPENAI_API_KEY")

        return len(missing) == 0, missing

    def validate_database(self) -> bool:
        """Check if database is configured."""
        return self.database.connection_string is not None


# ============================================================================
# Global Settings Instance
# ============================================================================

# Load settings from environment
settings = Settings.from_env()


# ============================================================================
# Helper Functions
# ============================================================================

def get_settings() -> Settings:
    """
    Get the global settings instance.

    Returns:
        Settings instance
    """
    return settings


def reload_settings() -> Settings:
    """
    Reload settings from environment variables.

    Returns:
        New Settings instance
    """
    global settings
    load_dotenv(override=True)
    settings = Settings.from_env()
    return settings


def print_settings(hide_sensitive: bool = True):
    """
    Print current settings (for debugging).

    Args:
        hide_sensitive: Hide sensitive values like API keys
    """
    import json

    config_dict = settings.to_dict()

    if hide_sensitive:
        # Remove sensitive fields
        if "security" in config_dict:
            config_dict["security"] = {
                "auth_enabled": config_dict["security"].get("auth_enabled", False)
            }

    print("\n" + "="*70)
    print("DEVFORK ARENA CONFIGURATION")
    print("="*70)
    print(json.dumps(config_dict, indent=2))
    print("="*70 + "\n")


def validate_configuration() -> tuple[bool, list[str]]:
    """
    Validate that all required configuration is present.

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []

    # Check API keys
    is_valid, missing_keys = settings.validate_api_keys()
    if not is_valid:
        errors.append(f"Missing API keys: {', '.join(missing_keys)}")

    # Check database (warning, not error)
    if not settings.validate_database():
        errors.append("Database not configured (TIGERDATA_CONNECTION_STRING not set)")

    # Validate environment
    valid_envs = ["development", "staging", "production"]
    if settings.environment not in valid_envs:
        errors.append(f"Invalid environment: {settings.environment}. Must be one of: {valid_envs}")

    return len(errors) == 0, errors


# ============================================================================
# Configuration Export
# ============================================================================

__all__ = [
    "Settings",
    "AgentConfig",
    "ModelConfig",
    "APIConfig",
    "DatabaseConfig",
    "CompetitionConfig",
    "LoggingConfig",
    "SecurityConfig",
    "settings",
    "get_settings",
    "reload_settings",
    "print_settings",
    "validate_configuration",
]
