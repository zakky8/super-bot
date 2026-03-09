import os
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "CryptoSentimentTracker/1.0")

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

CRYPTO_SUBREDDITS = [
    "CryptoCurrency", "bitcoin", "ethereum",
    "CryptoMarkets", "defi", "altcoin",
]

COIN_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "ADA": "cardano",
    "SOL": "solana",
    "BNB": "binancecoin",
}
