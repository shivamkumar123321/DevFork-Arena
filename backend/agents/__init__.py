"""
AI Agents module for DevFork Arena.

This module provides AI-powered agents that can autonomously solve coding challenges
using LangChain with Anthropic Claude and OpenAI models.

Main components:
    - BaseAgent: Abstract base class for all agents
    - ClaudeAgent: Agent powered by Anthropic's Claude models
    - OpenAIAgent: Agent powered by OpenAI's GPT models
    - AgentFactory: Factory for creating agents
    - CodeExecutor: Safe code execution and testing
"""

from .base_agent import BaseAgent
from .claude_agent import ClaudeAgent, create_claude_agent
from .openai_agent import OpenAIAgent, create_openai_agent
from .agent_factory import (
    AgentFactory,
    create_agent,
    create_default_agent,
    create_claude_agent as factory_create_claude,
    create_openai_agent as factory_create_openai
)
from .code_executor import CodeExecutor, executor

__all__ = [
    # Base class
    "BaseAgent",

    # Concrete agents
    "ClaudeAgent",
    "OpenAIAgent",

    # Factory
    "AgentFactory",
    "create_agent",
    "create_default_agent",

    # Convenience functions
    "create_claude_agent",
    "create_openai_agent",

    # Code execution
    "CodeExecutor",
    "executor",
]

__version__ = "1.0.0"
