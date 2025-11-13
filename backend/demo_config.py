"""
Configuration System Demo

Demonstrates how to use the centralized configuration system.
"""
import sys
sys.path.append('backend')

from config import (
    settings,
    get_settings,
    print_settings,
    validate_configuration,
    reload_settings
)


def demo_basic_usage():
    """Demonstrate basic configuration usage."""
    print("\n" + "="*70)
    print("BASIC CONFIGURATION USAGE")
    print("="*70 + "\n")

    # Access configuration sections
    print("Agent Configuration:")
    print(f"  Default temperature: {settings.agent.default_temperature}")
    print(f"  Max tokens: {settings.agent.default_max_tokens}")
    print(f"  Agent timeout: {settings.agent.agent_timeout_seconds}s")
    print(f"  Max retries: {settings.agent.max_retry_attempts}")

    print("\nModel Configuration:")
    print(f"  Default provider: {settings.model.default_provider}")
    print(f"  OpenAI model: {settings.model.openai_default_model}")
    print(f"  Claude model: {settings.model.anthropic_default_model}")

    print("\nAPI Configuration:")
    print(f"  Host: {settings.api.host}")
    print(f"  Port: {settings.api.port}")
    print(f"  CORS origins: {settings.api.cors_origins}")
    print(f"  Rate limit: {settings.api.rate_limit_requests} requests per {settings.api.rate_limit_window_seconds}s")

    print("\nCompetition Configuration:")
    print(f"  Min agents: {settings.competition.min_agents_per_competition}")
    print(f"  Max agents: {settings.competition.max_agents_per_competition}")
    print(f"  Default timeout: {settings.competition.default_competition_timeout}s")
    print(f"  Score base: {settings.competition.score_base}")


def demo_validation():
    """Demonstrate configuration validation."""
    print("\n" + "="*70)
    print("CONFIGURATION VALIDATION")
    print("="*70 + "\n")

    # Validate API keys
    is_valid, missing = settings.validate_api_keys()
    if is_valid:
        print("✓ All API keys are configured")
    else:
        print(f"✗ Missing API keys: {', '.join(missing)}")

    # Validate database
    if settings.validate_database():
        print("✓ Database is configured")
    else:
        print("✗ Database is not configured")

    # Full validation
    is_valid, errors = validate_configuration()
    if is_valid:
        print("\n✓ All configuration is valid!")
    else:
        print("\n✗ Configuration errors:")
        for error in errors:
            print(f"  - {error}")


def demo_environment_specific():
    """Demonstrate environment-specific configuration."""
    print("\n" + "="*70)
    print("ENVIRONMENT-SPECIFIC CONFIGURATION")
    print("="*70 + "\n")

    print(f"Current environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")

    if settings.environment == "development":
        print("\n📝 Development mode settings:")
        print("  - Auto-reload enabled")
        print("  - Detailed error messages")
        print("  - Debug logging")
    elif settings.environment == "production":
        print("\n🚀 Production mode settings:")
        print("  - Auto-reload disabled")
        print("  - Secure error messages")
        print("  - Info-level logging")


def demo_usage_in_code():
    """Show how to use configuration in actual code."""
    print("\n" + "="*70)
    print("USAGE IN CODE EXAMPLES")
    print("="*70 + "\n")

    print("Example 1: Creating an agent with config settings")
    print("-" * 70)
    print("""
from config import settings
from agents import create_default_agent

# Use configuration values
agent = create_default_agent(
    temperature=settings.agent.default_temperature,
    max_tokens=settings.agent.default_max_tokens,
    max_iterations=settings.agent.default_max_iterations
)
    """)

    print("\nExample 2: Using timeout settings")
    print("-" * 70)
    print("""
from config import settings
import asyncio

async def run_agent_with_timeout(agent, challenge):
    try:
        result = await asyncio.wait_for(
            agent.solve_challenge(challenge),
            timeout=settings.agent.agent_timeout_seconds
        )
        return result
    except asyncio.TimeoutError:
        print(f"Agent timed out after {settings.agent.agent_timeout_seconds}s")
    """)

    print("\nExample 3: Competition configuration")
    print("-" * 70)
    print("""
from config import settings

def validate_competition(agent_ids):
    min_agents = settings.competition.min_agents_per_competition
    max_agents = settings.competition.max_agents_per_competition

    if len(agent_ids) < min_agents:
        raise ValueError(f"Minimum {min_agents} agents required")
    if len(agent_ids) > max_agents:
        raise ValueError(f"Maximum {max_agents} agents allowed")
    """)

    print("\nExample 4: Model selection")
    print("-" * 70)
    print("""
from config import settings

def get_model_for_difficulty(difficulty: str) -> str:
    if difficulty == "easy":
        return settings.model.openai_fast_model  # gpt-3.5-turbo
    elif difficulty == "hard":
        return settings.model.openai_powerful_model  # gpt-4
    else:
        return settings.model.openai_default_model  # gpt-4-turbo
    """)

    print("\nExample 5: Rate limiting")
    print("-" * 70)
    print("""
from config import settings
from fastapi import FastAPI
from slowapi import Limiter

app = FastAPI()

if settings.api.rate_limit_enabled:
    limiter = Limiter(
        key_func=lambda: "global",
        default_limits=[
            f"{settings.api.rate_limit_requests}/"
            f"{settings.api.rate_limit_window_seconds}seconds"
        ]
    )
    app.state.limiter = limiter
    """)


def demo_print_settings():
    """Show how to print all settings."""
    print("\n" + "="*70)
    print("PRINT ALL SETTINGS")
    print("="*70)

    # Print with sensitive data hidden
    print_settings(hide_sensitive=True)


def demo_dynamic_reload():
    """Demonstrate reloading configuration."""
    print("\n" + "="*70)
    print("DYNAMIC CONFIGURATION RELOAD")
    print("="*70 + "\n")

    print("Current temperature:", settings.agent.default_temperature)

    print("\nTo reload configuration from .env:")
    print("  1. Modify .env file")
    print("  2. Call reload_settings()")
    print("  3. Settings will be reloaded from environment")

    print("\nExample:")
    print("""
from config import reload_settings

# After modifying .env
new_settings = reload_settings()
print(f"New temperature: {new_settings.agent.default_temperature}")
    """)


def show_menu():
    """Show interactive menu."""
    print("\n" + "="*70)
    print("CONFIGURATION SYSTEM DEMO")
    print("="*70 + "\n")

    print("Choose a demo:")
    print("1. Basic Usage")
    print("2. Configuration Validation")
    print("3. Environment-Specific Settings")
    print("4. Usage in Code Examples")
    print("5. Print All Settings")
    print("6. Dynamic Reload")
    print("7. Run All Demos")
    print("0. Exit\n")


def main():
    """Main demo function."""
    while True:
        show_menu()
        choice = input("Enter choice (0-7): ").strip()

        if choice == "1":
            demo_basic_usage()
        elif choice == "2":
            demo_validation()
        elif choice == "3":
            demo_environment_specific()
        elif choice == "4":
            demo_usage_in_code()
        elif choice == "5":
            demo_print_settings()
        elif choice == "6":
            demo_dynamic_reload()
        elif choice == "7":
            demo_basic_usage()
            demo_validation()
            demo_environment_specific()
            demo_usage_in_code()
            demo_print_settings()
            demo_dynamic_reload()
        elif choice == "0":
            print("\nExiting...")
            break
        else:
            print("Invalid choice!")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
