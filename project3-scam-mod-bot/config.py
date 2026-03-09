import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# B20 FIX: safe int conversion — empty string or missing env var returns None, not crash
def _safe_int(value: str | None) -> int | None:
    try:
        return int(value) if value and value.strip() else None
    except (ValueError, TypeError):
        return None

# B22 FIX: LOG_CHANNEL_ID lives in config, not scattered in discord_mod.py
LOG_CHANNEL_ID: int | None = _safe_int(os.getenv("LOG_CHANNEL_ID"))
