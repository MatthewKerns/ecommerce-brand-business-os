"""
Base Agent Class for AI Content Generation
All specialized agents inherit from this class
"""
import anthropic
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json

from config.config import (
    ANTHROPIC_API_KEY,
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    BRAND_VOICE_PATH,
    BRAND_STRATEGY_PATH,
    CONTENT_STRATEGY_PATH,
    VALUE_PROP_PATH,
    TARGET_MARKET_PATH,
    BRAND_NAME,
    BRAND_TAGLINE,
    BRAND_PROMISE
)
from logging_config import get_logger
from exceptions import (
    AgentInitializationError,
    ContentGenerationError,
    BrandContextLoadError,
    AnthropicAPIError,
    AuthenticationError,
    RateLimitError
)


class BaseAgent:
    """Base class for all content generation agents"""

    def __init__(self, agent_name: str, model: str = DEFAULT_MODEL):
        """
        Initialize the base agent

        Args:
            agent_name: Name of the specialized agent
            model: Claude model to use

        Raises:
            AgentInitializationError: If agent initialization fails
        """
        self.agent_name = agent_name
        self.model = model
        self.logger = get_logger(f"agent.{agent_name}")

        try:
            self.logger.info(f"Initializing {agent_name} agent with model {model}")

            if not ANTHROPIC_API_KEY:
                raise AuthenticationError("Anthropic")

            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            self.brand_context = self._load_brand_context()

            self.logger.info(f"Successfully initialized {agent_name} agent")
        except AuthenticationError:
            self.logger.error(f"Authentication failed for {agent_name} agent", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize {agent_name} agent: {e}", exc_info=True)
            raise AgentInitializationError(agent_name, str(e))

    def _load_brand_context(self) -> Dict[str, str]:
        """
        Load all brand context files

        Returns:
            Dictionary containing brand context information

        Raises:
            BrandContextLoadError: If critical brand files cannot be loaded
        """
        self.logger.debug("Loading brand context files")

        context = {
            "brand_name": BRAND_NAME,
            "tagline": BRAND_TAGLINE,
            "promise": BRAND_PROMISE
        }

        # Load brand voice guide
        try:
            if BRAND_VOICE_PATH.exists():
                context["brand_voice"] = BRAND_VOICE_PATH.read_text()
                self.logger.debug(f"Loaded brand voice from {BRAND_VOICE_PATH}")
            else:
                self.logger.warning(f"Brand voice file not found: {BRAND_VOICE_PATH}")
        except Exception as e:
            raise BrandContextLoadError(str(BRAND_VOICE_PATH), str(e))

        # Load brand strategy
        try:
            if BRAND_STRATEGY_PATH.exists():
                context["brand_strategy"] = BRAND_STRATEGY_PATH.read_text()
                self.logger.debug(f"Loaded brand strategy from {BRAND_STRATEGY_PATH}")
            else:
                self.logger.warning(f"Brand strategy file not found: {BRAND_STRATEGY_PATH}")
        except Exception as e:
            raise BrandContextLoadError(str(BRAND_STRATEGY_PATH), str(e))

        # Load content strategy
        try:
            if CONTENT_STRATEGY_PATH.exists():
                context["content_strategy"] = CONTENT_STRATEGY_PATH.read_text()
                self.logger.debug(f"Loaded content strategy from {CONTENT_STRATEGY_PATH}")
            else:
                self.logger.warning(f"Content strategy file not found: {CONTENT_STRATEGY_PATH}")
        except Exception as e:
            raise BrandContextLoadError(str(CONTENT_STRATEGY_PATH), str(e))

        # Load value proposition
        try:
            if VALUE_PROP_PATH.exists():
                context["value_proposition"] = VALUE_PROP_PATH.read_text()
                self.logger.debug(f"Loaded value proposition from {VALUE_PROP_PATH}")
            else:
                self.logger.warning(f"Value proposition file not found: {VALUE_PROP_PATH}")
        except Exception as e:
            raise BrandContextLoadError(str(VALUE_PROP_PATH), str(e))

        # Load target market
        try:
            if TARGET_MARKET_PATH.exists():
                context["target_market"] = TARGET_MARKET_PATH.read_text()
                self.logger.debug(f"Loaded target market from {TARGET_MARKET_PATH}")
            else:
                self.logger.warning(f"Target market file not found: {TARGET_MARKET_PATH}")
        except Exception as e:
            raise BrandContextLoadError(str(TARGET_MARKET_PATH), str(e))

        self.logger.info(f"Loaded {len(context)} brand context items")
        return context

    def _build_system_prompt(self, additional_context: str = "") -> str:
        """
        Build the system prompt with brand context

        Args:
            additional_context: Additional context specific to the agent

        Returns:
            Complete system prompt
        """
        base_prompt = f"""You are an expert content creator for {BRAND_NAME}, a TCG storage brand.

BRAND IDENTITY:
- Name: {BRAND_NAME}
- Tagline: {BRAND_TAGLINE}
- Promise: {BRAND_PROMISE}

BRAND VOICE & STRATEGY:
{self.brand_context.get('brand_voice', 'Not loaded')}

BRAND STRATEGY:
{self.brand_context.get('brand_strategy', 'Not loaded')}

TARGET MARKET:
{self.brand_context.get('target_market', 'Not loaded')}

VALUE PROPOSITION:
{self.brand_context.get('value_proposition', 'Not loaded')}

{additional_context}

Your role is to create content that:
1. Stays true to the brand voice (confident but not arrogant, passionate about gaming culture)
2. Speaks the language of fantasy and battle readiness
3. Positions products as battle-ready equipment, NOT commodity storage
4. Connects with the emotional identity of serious TCG players
5. Maintains the "Show Up Battle Ready" mindset in every piece

Always create content that makes customers feel like serious players, not casual hobbyists."""

        return base_prompt

    def generate_content(
        self,
        prompt: str,
        system_context: str = "",
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = 1.0
    ) -> str:
        """
        Generate content using Claude API

        Args:
            prompt: The user prompt for content generation
            system_context: Additional system context beyond base brand context
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (0-1)

        Returns:
            Generated content as string

        Raises:
            ContentGenerationError: If content generation fails
            AnthropicAPIError: If API call fails
            RateLimitError: If rate limit is exceeded
        """
        self.logger.info(f"Generating content with prompt length: {len(prompt)} chars")
        self.logger.debug(f"Model: {self.model}, max_tokens: {max_tokens}, temperature: {temperature}")

        system_prompt = self._build_system_prompt(system_context)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = message.content[0].text
            self.logger.info(f"Successfully generated {len(content)} chars of content")
            self.logger.debug(f"Content preview: {content[:100]}...")

            return content

        except anthropic.RateLimitError as e:
            self.logger.error("Rate limit exceeded", exc_info=True)
            raise RateLimitError(retry_after=getattr(e, 'retry_after', None))
        except anthropic.AuthenticationError as e:
            self.logger.error("Authentication failed", exc_info=True)
            raise AuthenticationError("Anthropic")
        except anthropic.APIError as e:
            self.logger.error(f"Anthropic API error: {e}", exc_info=True)
            raise AnthropicAPIError(
                status_code=getattr(e, 'status_code', None),
                response_body=str(e)
            )
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}", exc_info=True)
            raise ContentGenerationError(self.agent_name, prompt, str(e))

    def save_output(
        self,
        content: str,
        output_dir: Path,
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save generated content to file

        Args:
            content: The generated content
            output_dir: Directory to save to
            filename: Optional specific filename (will generate if not provided)
            metadata: Optional metadata to save alongside content

        Returns:
            Path to saved file

        Raises:
            IOError: If file writing fails
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{self.agent_name}_{timestamp}.md"

            output_path = output_dir / filename
            self.logger.debug(f"Saving content to {output_path}")

            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            output_path.write_text(content)
            self.logger.info(f"Content saved to: {output_path}")

            # Save metadata if provided
            if metadata:
                metadata_path = output_dir / f"{output_path.stem}_metadata.json"
                metadata_path.write_text(json.dumps(metadata, indent=2))
                self.logger.debug(f"Metadata saved to: {metadata_path}")

            return output_path

        except Exception as e:
            self.logger.error(f"Failed to save output to {output_path}: {e}", exc_info=True)
            raise

    def generate_and_save(
        self,
        prompt: str,
        output_dir: Path,
        system_context: str = "",
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> tuple[str, Path]:
        """
        Generate content and save it in one call

        Args:
            prompt: The user prompt
            output_dir: Where to save
            system_context: Additional system context
            filename: Optional filename
            metadata: Optional metadata
            **kwargs: Additional args for generate_content

        Returns:
            Tuple of (generated_content, output_path)

        Raises:
            ContentGenerationError: If content generation fails
            IOError: If file writing fails
        """
        self.logger.info(f"Starting generate_and_save workflow")

        content = self.generate_content(prompt, system_context, **kwargs)
        path = self.save_output(content, output_dir, filename, metadata)

        self.logger.info(f"Completed generate_and_save workflow: {path}")
        return content, path
