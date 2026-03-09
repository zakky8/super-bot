import time
import requests
from loguru import logger
from config import COINGECKO_BASE, COIN_IDS


def get_prices(coins: list[str] | None = None) -> dict:
    """
    Fetch current prices from CoinGecko free API.
    B14 FIX: Retry on 429 with exponential backoff.
    Cached in Streamlit with ttl=3600 to avoid hitting rate limits.
    """
    if coins is None:
        coins = list(COIN_IDS.keys())

    ids = [COIN_IDS[c] for c in coins if c in COIN_IDS]
    if not ids:
        return {}

    for attempt in range(3):
        try:
            resp = requests.get(
                f"{COINGECKO_BASE}/simple/price",
                params={
                    "ids": ",".join(ids),
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_market_cap": "true",
                },
                timeout=10,
            )
            if resp.status_code == 429:
                wait = 60 * (attempt + 1)
                logger.warning(f"CoinGecko rate limited — retry in {wait}s (attempt {attempt + 1}/3)")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.Timeout:
            logger.error("CoinGecko request timed out")
            return {}
        except requests.exceptions.RequestException as e:
            logger.error(f"CoinGecko request failed: {e}")
            return {}

    logger.error("CoinGecko: all retries exhausted")
    return {}
