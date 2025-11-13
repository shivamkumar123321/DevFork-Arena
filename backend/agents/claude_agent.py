"""
Claude Agent Implementation using Anthropic's Claude models via LangChain.

This module provides a concrete implementation of the BaseAgent for Anthropic's Claude models.
"""
import os
import logging
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage

from base_agent import BaseAgent
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import AgentConfig

logger = logging.getLogger(__name__)


class ClaudeAgent(BaseAgent):
    """
    AI Agent powered by Anthropic's Claude models.

    This agent uses Claude (e.g., Claude 3.5 Sonnet) to solve coding challenges
    through LangChain's Anthropic integration.

    Supported models:
    - claude-3-5-sonnet-20241022 (latest, most capable)
    - claude-3-opus-20240229 (powerful, slower)
    - claude-3-sonnet-20240229 (balanced)
    - claude-3-haiku-20240307 (fast, economical)
    """

    DEFAULT_SYSTEM_PROMPT = """You are an expert software engineer with deep knowledge of algorithms,
data structures, and Python programming. You excel at solving coding challenges efficiently and
correctly. You write clean, well-tested code that handles edge cases properly.

When solving problems:
1. Analyze the problem carefully to understand requirements
2. Consider edge cases and constraints
3. Choose efficient algorithms and data structures
4. Write clean, readable Python code
5. Ensure your solution is correct and complete

Always provide only the code without explanations unless specifically asked."""

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize Claude agent.

        Args:
            config: AgentConfig instance. If None, uses default configuration.
        """
        if config is None:
            config = AgentConfig(
                name="Claude Solver",
                model_provider="anthropic",
                model_name="claude-3-5-sonnet-20241022",
                temperature=0.7,
                max_tokens=4096,
                max_iterations=3
            )

        # Ensure model provider is set correctly
        config.model_provider = "anthropic"

        super().__init__(config)

    def _initialize_llm(self):
        """
        Initialize the Claude language model via LangChain.

        Raises:
            ValueError: If ANTHROPIC_API_KEY is not set
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Please set it in your .env file."
            )

        try:
            self.llm = ChatAnthropic(
                model=self.config.model_name,
                anthropic_api_key=api_key,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            logger.info(f"Initialized Claude model: {self.config.model_name}")

        except Exception as e:
            logger.error(f"Failed to initialize Claude model: {str(e)}")
            raise

    async def _generate_code(self, prompt: str) -> str:
        """
        Generate code using Claude.

        Args:
            prompt: The prompt describing what code to generate

        Returns:
            str: Generated Python code

        Raises:
            Exception: If code generation fails
        """
        try:
            # Use system prompt if configured, otherwise use default
            system_prompt = self.config.system_prompt or self.DEFAULT_SYSTEM_PROMPT

            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]

            logger.info(f"Generating code with {self.config.model_name}...")

            # Generate response
            response = await self.llm.ainvoke(messages)

            # Extract code from response
            raw_code = response.content
            code = self._extract_code_from_response(raw_code)

            logger.info(f"Generated {len(code)} characters of code")
            logger.debug(f"Generated code:\n{code}")

            return code

        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            raise Exception(f"Failed to generate code with Claude: {str(e)}")

    def get_model_info(self) -> dict:
        """
        Get information about the current Claude model.

        Returns:
            dict: Model information including name, provider, and configuration
        """
        return {
            "name": self.config.name,
            "provider": "anthropic",
            "model": self.config.model_name,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "max_iterations": self.config.max_iterations
        }


# Convenience function to create a Claude agent with common configurations
def create_claude_agent(
    model_name: str = "claude-3-5-sonnet-20241022",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    max_iterations: int = 3,
    name: str = "Claude Solver"
) -> ClaudeAgent:
    """
    Factory function to create a Claude agent with custom configuration.

    Args:
        model_name: Claude model to use
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens to generate
        max_iterations: Maximum solution attempts
        name: Agent name

    Returns:
        ClaudeAgent: Configured Claude agent instance

    Example:
        >>> agent = create_claude_agent(
        ...     model_name="claude-3-5-sonnet-20241022",
        ...     temperature=0.5,
        ...     max_iterations=5
        ... )
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
