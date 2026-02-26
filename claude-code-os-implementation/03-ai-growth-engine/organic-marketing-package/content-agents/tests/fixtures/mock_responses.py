"""
Mock Anthropic API Responses for Testing

This module provides realistic mock responses that mimic the Anthropic API structure.
Used to test agents without making actual API calls.
"""

from unittest.mock import Mock
from typing import List, Dict, Any


class MockTextBlock:
    """Mock for Anthropic API text content block"""
    def __init__(self, text: str):
        self.text = text
        self.type = "text"


class MockMessage:
    """Mock for Anthropic API message response"""
    def __init__(
        self,
        content: List[MockTextBlock],
        model: str = "claude-sonnet-4-20250514",
        role: str = "assistant",
        stop_reason: str = "end_turn",
        usage: Dict[str, int] = None
    ):
        self.content = content
        self.model = model
        self.role = role
        self.stop_reason = stop_reason
        self.id = "msg_test_123"
        self.type = "message"
        self.usage = usage or {
            "input_tokens": 100,
            "output_tokens": 200
        }


# Blog content mock responses
MOCK_BLOG_RESPONSE = MockMessage(
    content=[MockTextBlock(text="""# Essential Gear for Tactical Readiness

In the world of competitive TCG, being battle-ready isn't just about knowing your deck—it's about having the right gear to protect and organize your arsenal. Today, we're breaking down the essential equipment every serious player needs.

## The Foundation: Premium Storage

Your cards are your weapons. Treat them accordingly. Quality deck boxes aren't optional—they're mission-critical equipment that keeps your strategies protected and deployment-ready.

## Organization is Strategy

Serious players know that fumbling for cards mid-tournament is the mark of an amateur. Invest in modular storage solutions that let you access any card in your collection instantly.

## Show Up Battle Ready

Every tournament, every game night, every casual match—arrive with gear that announces you're here to compete. Your equipment speaks before you shuffle your first hand.""")]
)

MOCK_SOCIAL_RESPONSE = MockMessage(
    content=[MockTextBlock(text="""🎯 Daily EDC Essentials for TCG Champions

Your deck box isn't just storage—it's your battle station. Here's what separates serious players from casual collectors:

✅ Premium deck protection
✅ Quick-access organization
✅ Tournament-grade durability
✅ Command-ready presentation

What's in your battle kit? Drop it below! 👇

#TCG #EDC #BattleReady #ShowUpReady""")]
)

MOCK_EMAIL_RESPONSE = MockMessage(
    content=[MockTextBlock(text="""Subject: Your Deck Deserves Battle-Ready Protection

Hey Champion,

Every serious TCG player knows the difference between casual storage and battle-ready gear. Your cards represent hours of strategy, careful collection, and significant investment.

Don't leave them vulnerable to the chaos of tournament play.

Our premium storage solutions are engineered for one purpose: keeping your arsenal organized, protected, and deployment-ready. No fumbling. No damage. No excuses.

This week only, we're offering 20% off our complete storage system. It's time to upgrade from amateur hour to tournament-grade protection.

Show up battle ready.

[Shop Now]

Ready when you are,
The BattleVault Team""")]
)

MOCK_VIDEO_SCRIPT_RESPONSE = MockMessage(
    content=[MockTextBlock(text="""[HOOK - First 3 seconds]
Visual: Close-up of premium deck box opening with satisfying click
Voiceover: "Casual players store cards. Champions protect arsenals."

[PROBLEM - Seconds 4-10]
Visual: Montage of damaged cards, messy storage, tournament fumbling
Voiceover: "Your deck is your strategy. Why trust it to cheap storage?"

[SOLUTION - Seconds 11-25]
Visual: Smooth product showcase highlighting premium features
Voiceover: "BattleVault: Tournament-grade protection for serious players. Modular organization. Battle-ready durability. Command presence."

[CALL TO ACTION - Seconds 26-30]
Visual: Product with discount badge, website URL
Voiceover: "Don't just store your deck. Protect your arsenal. BattleVault - Show Up Battle Ready."

[End card with discount code]""")]
)

MOCK_AMAZON_RESPONSE = MockMessage(
    content=[MockTextBlock(text="""OPTION 1: Premium Trading Card Binder - Battle-Ready 9-Pocket Pages - Scratch-Resistant Storage for Pokemon, MTG, Sports Cards - Professional Tournament-Grade with Lifetime Warranty

OPTION 2: Tournament-Grade Trading Card Binder - Premium Scratch-Resistant Protection - 9-Pocket Battle-Ready Storage for Pokemon, MTG, Yu-Gi-Oh - Lifetime Warranty Included

OPTION 3: Battle-Ready Trading Card Storage Binder - Professional 9-Pocket Scratch-Resistant Pages - Premium Protection for Pokemon, MTG, Sports Cards - Tournament-Grade Quality

RECOMMENDED: Option 1 - It front-loads "Premium" as the value signal, clearly states the category (Trading Card Binder), highlights the battle-ready positioning, and includes the lifetime warranty which is a strong trust signal.""")]
)

MOCK_COMPETITOR_RESPONSE = MockMessage(
    content=[MockTextBlock(text="""## COMPETITOR OVERVIEW
This competitor positions themselves as a mid-tier storage solution, focusing primarily on affordability and basic functionality rather than premium quality or identity-driven positioning.

## DETAILED ANALYSIS

### Positioning Analysis
The competitor uses commodity positioning - emphasizing price point and basic features rather than aspirational identity or premium quality signals.

### Keyword Strategy
Front-loaded keywords include "storage" and "organizer" - functional but not emotionally resonant. Missing opportunity to target "tournament," "professional," or "battle-ready" terminology.

### Messaging Analysis
Benefits-to-features ratio is approximately 30:70, heavily weighted toward features. Brand voice is neutral and informational rather than inspiring or identity-driven.

## STRENGTHS
- Clear product specifications
- Competitive pricing strategy
- Good use of bullet point structure

## WEAKNESSES
- Commodity positioning leaves them vulnerable to premium competitors
- No emotional connection or identity positioning
- Generic language that doesn't resonate with serious players
- Weak warranty offering (90 days vs. our lifetime)

## DIFFERENTIATION STRATEGY
Infinity Vault should emphasize:
1. Battle-ready positioning (not just storage)
2. Professional/tournament-grade quality signals
3. Identity-driven messaging (serious players, not casual collectors)
4. Lifetime warranty as trust builder
5. Premium materials and construction

## ACTION ITEMS
1. Highlight lifetime warranty prominently
2. Use battle-ready language throughout
3. Position as professional equipment, not commodity storage
4. Emphasize tournament-tested durability
5. Create emotional connection with serious player identity""")]
)

# Error scenario mock responses
MOCK_API_ERROR = Exception("API rate limit exceeded")
MOCK_TIMEOUT_ERROR = Exception("Request timeout")
MOCK_INVALID_RESPONSE = MockMessage(
    content=[],  # Empty content to test error handling
)


def create_mock_response(text: str, **kwargs) -> MockMessage:
    """
    Create a custom mock response with given text

    Args:
        text: The response text content
        **kwargs: Additional MockMessage parameters

    Returns:
        MockMessage instance
    """
    return MockMessage(
        content=[MockTextBlock(text=text)],
        **kwargs
    )


def create_mock_client(response: MockMessage = None) -> Mock:
    """
    Create a mock Anthropic client with configurable response

    Args:
        response: MockMessage to return (defaults to MOCK_BLOG_RESPONSE)

    Returns:
        Mock client object
    """
    if response is None:
        response = MOCK_BLOG_RESPONSE

    mock_client = Mock()
    mock_client.messages.create.return_value = response
    return mock_client


def create_error_client(error: Exception) -> Mock:
    """
    Create a mock client that raises an error

    Args:
        error: Exception to raise

    Returns:
        Mock client that raises the error
    """
    mock_client = Mock()
    mock_client.messages.create.side_effect = error
    return mock_client
