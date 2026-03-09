# Project 5 — Crypto Sentiment Tracker

> Live crypto sentiment dashboard using Reddit PRAW + CoinGecko + VADER/TextBlob. Tracks public sentiment and live prices in real time.

## What It Does
- Fetches live Reddit posts from 6 crypto subreddits
- Analyzes sentiment using VADER (primary) + TextBlob (near-neutral tiebreaker)
- Displays live CoinGecko prices with 24h change
- Interactive Streamlit dashboard with pie chart + time series
- 1-hour cache prevents API rate limiting

## Tech Stack
- Python 3.12
- praw 7.7.1 (Reddit)
- vaderSentiment 3.3.2 + textblob 0.18.0
- streamlit 1.55.0 + plotly 5.24.1
- Deployed on: Streamlit Cloud (free)

## Setup

1. Install: `cd project5-sentiment-tracker && pip install -r requirements.txt`
2. Setup NLTK: `python setup.py`
3. Configure: `cp .env.example .env` — fill in Reddit API credentials
4. Start: `streamlit run dashboard.py`

## Architecture
VADER handles ~90% of messages at near-zero cost. TextBlob is only invoked when VADER score is near-neutral (-0.1 to 0.1). Both analyzers initialized as module-level singletons.
