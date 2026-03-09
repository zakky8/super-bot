import json
import re
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger

# Hardcoded minimal fallback in case JSON file is missing
_FALLBACK_PATTERNS = {
    "high_risk_phrases": ["seed phrase", "private key", "connect your wallet to claim"],
    "suspicious_domains": ["bit.ly", "tinyurl.com"],
    "trusted_role_ids": [],
    "wallet_regex": "0x[a-fA-F0-9]{40}",
}


class RiskLevel(Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    HIGH_RISK = "high_risk"


@dataclass
class DetectionResult:
    risk_level: RiskLevel
    reasons: list[str] = field(default_factory=list)
    original_message: str = ""


def _load_patterns() -> dict:
    # B3 FIX: guarded load with hardcoded fallback
    try:
        with open("scam_patterns.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("scam_patterns.json not found — using hardcoded fallback patterns")
        return _FALLBACK_PATTERNS


PATTERNS = _load_patterns()

# B11 FIX: compile regex ONCE at module load
_WALLET_RE = re.compile(PATTERNS["wallet_regex"], re.IGNORECASE)
_DOMAIN_RE = re.compile(
    "|".join(re.escape(d) for d in PATTERNS["suspicious_domains"]),
    re.IGNORECASE,
)


def reload_patterns() -> None:
    """Hot-reload patterns from disk without restarting the bot."""
    global PATTERNS, _WALLET_RE, _DOMAIN_RE
    PATTERNS = _load_patterns()
    _WALLET_RE = re.compile(PATTERNS["wallet_regex"], re.IGNORECASE)
    _DOMAIN_RE = re.compile(
        "|".join(re.escape(d) for d in PATTERNS["suspicious_domains"]),
        re.IGNORECASE,
    )
    logger.info("Scam patterns reloaded from disk")


def detect_scam(
    message: str, author_role_ids: list[int] | None = None
) -> DetectionResult:
    """
    Fast pattern-based scam detection.
    L3: Skips trusted roles. L4: Pre-compiled regex.
    """
    # Allowlist: skip trusted roles immediately
    if author_role_ids:
        trusted = set(PATTERNS.get("trusted_role_ids", []))
        if trusted and trusted.intersection(set(author_role_ids)):
            return DetectionResult(RiskLevel.SAFE, [], message)

    lower = message.lower()
    reasons: list[str] = []

    for phrase in PATTERNS["high_risk_phrases"]:
        if phrase in lower:
            reasons.append(f"High-risk phrase: '{phrase}'")

    domain_hits = _DOMAIN_RE.findall(message)
    if domain_hits:
        reasons.append(f"Suspicious domain(s): {', '.join(set(domain_hits))}")

    wallet_hits = _WALLET_RE.findall(message)
    if wallet_hits:
        reasons.append(f"Wallet address(es) detected: {len(wallet_hits)}")

    if len(reasons) >= 2:
        return DetectionResult(RiskLevel.HIGH_RISK, reasons, message)
    if len(reasons) == 1:
        return DetectionResult(RiskLevel.SUSPICIOUS, reasons, message)
    return DetectionResult(RiskLevel.SAFE, [], message)
