import anthropic
from loguru import logger

from config import ANTHROPIC_API_KEY
from pattern_detector import RiskLevel

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

_SYSTEM = (
    "You are a crypto community safety system. "
    "Analyze the message and respond with ONLY one word: SAFE, SUSPICIOUS, or SCAM. "
    "No punctuation. No explanation. Just one word."
)


async def ai_classify_message(message: str) -> RiskLevel:
    """
    AI second-opinion for SUSPICIOUS messages only.
    L3 FIX: ALL failure paths default to SUSPICIOUS — never SAFE.
    """
    try:
        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=5,
            system=_SYSTEM,
            messages=[{"role": "user", "content": message[:500]}],
        )
        result = response.content[0].text.strip().upper()
        logger.debug(f"AI scam verdict: '{result}'")

        if result == "SCAM":
            return RiskLevel.HIGH_RISK
        if result == "SUSPICIOUS":
            return RiskLevel.SUSPICIOUS
        return RiskLevel.SAFE

    except anthropic.RateLimitError:
        logger.warning("AI classifier rate limited — defaulting to SUSPICIOUS")
        return RiskLevel.SUSPICIOUS
    except Exception as e:
        logger.error(f"AI classifier error: {e} — defaulting to SUSPICIOUS")
        return RiskLevel.SUSPICIOUS
