"""
Agent Factory for creating AI agents.

This module provides a factory pattern for creating different types of AI agents
based on configuration or provider name.
"""
import logging
from typing import Optional, Union

from claude_agent import ClaudeAgent
from openai_agent import OpenAIAgent
from base_agent import BaseAgent

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import AgentConfig

logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Factory class for creating AI agents.

    This factory supports creating different types of agents based on
    provider name or configuration.
    """

    SUPPORTED_PROVIDERS = {
        "anthropic": ClaudeAgent,
        "claude": ClaudeAgent,
        "openai": OpenAIAgent,
        "gpt": OpenAIAgent,
    }

    @staticmethod
    def create_agent(
        provider: str,
        config: Optional[AgentConfig] = None,
        **kwargs
    ) -> BaseAgent:
        """
        Create an agent based on provider name.

        Args:
            provider: Provider name ('anthropic', 'claude', 'openai', 'gpt')
            config: Optional AgentConfig. If None, will create from kwargs
            **kwargs: Additional configuration parameters if config is None

        Returns:
            BaseAgent: Instance of the requested agent type

        Raises:
            ValueError: If provider is not supported

        Example:
            >>> agent = AgentFactory.create_agent('claude')
            >>> agent = AgentFactory.create_agent('openai', temperature=0.5)
        """
        provider_lower = provider.lower()

        if provider_lower not in AgentFactory.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: {list(AgentFactory.SUPPORTED_PROVIDERS.keys())}"
            )

        agent_class = AgentFactory.SUPPORTED_PROVIDERS[provider_lower]

        # If config is provided, use it directly
        if config:
            return agent_class(config)

        # Otherwise, create config from kwargs
        if kwargs:
            # Determine model name based on provider if not specified
            if 'model_name' not in kwargs:
                if provider_lower in ['anthropic', 'claude']:
                    kwargs['model_name'] = 'claude-3-5-sonnet-20241022'
                else:
                    kwargs['model_name'] = 'gpt-4-turbo-preview'

            # Set provider
            if provider_lower in ['anthropic', 'claude']:
                kwargs['model_provider'] = 'anthropic'
            else:
                kwargs['model_provider'] = 'openai'

            # Create name if not provided
            if 'name' not in kwargs:
                kwargs['name'] = f"{provider.capitalize()} Solver"

            config = AgentConfig(**kwargs)
            return agent_class(config)

        # No config or kwargs - use defaults
        return agent_class()

    @staticmethod
    def create_claude_agent(
        model_name: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        max_iterations: int = 3,
        name: str = "Claude Solver"
    ) -> ClaudeAgent:
        """
        Convenience method to create a Claude agent.

        Args:
            model_name: Claude model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            max_iterations: Maximum solution attempts
            name: Agent name

        Returns:
            ClaudeAgent: Configured Claude agent
        """
        config = AgentConfig(
            name=name,
            model_provider="anthropic",
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            max_iterations=max_iterations
        )
        return ClaudeAgent(config)

    @staticmethod
    def create_openai_agent(
        model_name: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        max_iterations: int = 3,
        name: str = "GPT-4 Solver"
    ) -> OpenAIAgent:
        """
        Convenience method to create an OpenAI agent.

        Args:
            model_name: OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            max_iterations: Maximum solution attempts
            name: Agent name

        Returns:
            OpenAIAgent: Configured OpenAI agent
        """
        config = AgentConfig(
            name=name,
            model_provider="openai",
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            max_iterations=max_iterations
        )
        return OpenAIAgent(config)

    @staticmethod
    def list_supported_providers() -> list:
        """
        Get list of supported agent providers.

        Returns:
            list: List of supported provider names
        """
        return list(AgentFactory.SUPPORTED_PROVIDERS.keys())

    @staticmethod
    def create_default_agent(**kwargs) -> OpenAIAgent:
        """
        Create a default agent (OpenAI GPT-4 Turbo).

        Args:
            **kwargs: Configuration parameters

        Returns:
            OpenAIAgent: Configured OpenAI agent
        """
        return AgentFactory.create_openai_agent(**kwargs)


# Convenience functions at module level
def create_agent(provider: str = "openai", **kwargs) -> BaseAgent:
    """
    Create an agent using the factory.

    Args:
        provider: Provider name (defaults to 'openai')
        **kwargs: Configuration parameters

    Returns:
        BaseAgent: Configured agent instance
    """
    return AgentFactory.create_agent(provider, **kwargs)


def create_claude_agent(**kwargs) -> ClaudeAgent:
    """Create a Claude agent."""
    return AgentFactory.create_claude_agent(**kwargs)


def create_openai_agent(**kwargs) -> OpenAIAgent:
    """Create an OpenAI agent."""
    return AgentFactory.create_openai_agent(**kwargs)


def create_default_agent(**kwargs) -> OpenAIAgent:
    """Create a default agent (OpenAI GPT-4 Turbo)."""
    return AgentFactory.create_default_agent(**kwargs)
