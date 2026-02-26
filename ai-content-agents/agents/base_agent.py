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


class BaseAgent:
    """Base class for all content generation agents"""

    def __init__(self, agent_name: str, model: str = DEFAULT_MODEL):
        """
        Initialize the base agent

        Args:
            agent_name: Name of the specialized agent
            model: Claude model to use
        """
        self.agent_name = agent_name
        self.model = model
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.brand_context = self._load_brand_context()

    def _load_brand_context(self) -> Dict[str, str]:
        """Load all brand context files"""
        context = {
            "brand_name": BRAND_NAME,
            "tagline": BRAND_TAGLINE,
            "promise": BRAND_PROMISE
        }

        # Load brand voice guide
        if BRAND_VOICE_PATH.exists():
            context["brand_voice"] = BRAND_VOICE_PATH.read_text()

        # Load brand strategy
        if BRAND_STRATEGY_PATH.exists():
            context["brand_strategy"] = BRAND_STRATEGY_PATH.read_text()

        # Load content strategy
        if CONTENT_STRATEGY_PATH.exists():
            context["content_strategy"] = CONTENT_STRATEGY_PATH.read_text()

        # Load value proposition
        if VALUE_PROP_PATH.exists():
            context["value_proposition"] = VALUE_PROP_PATH.read_text()

        # Load target market
        if TARGET_MARKET_PATH.exists():
            context["target_market"] = TARGET_MARKET_PATH.read_text()

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
        """
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

            return message.content[0].text

        except Exception as e:
            print(f"Error generating content: {e}")
            raise

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
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.agent_name}_{timestamp}.md"

        output_path = output_dir / filename
        output_path.write_text(content)

        # Save metadata if provided
        if metadata:
            metadata_path = output_dir / f"{output_path.stem}_metadata.json"
            metadata_path.write_text(json.dumps(metadata, indent=2))

        print(f"✓ Content saved to: {output_path}")
        return output_path

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
        """
        content = self.generate_content(prompt, system_context, **kwargs)
        path = self.save_output(content, output_dir, filename, metadata)
        return content, path
