import praw
import pandas as pd
from datetime import datetime
from loguru import logger
from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT, CRYPTO_SUBREDDITS,
)


def get_client() -> praw.Reddit:
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )


def fetch_posts(keywords: list[str], limit: int = 100) -> pd.DataFrame:
    """
    Fetch recent Reddit posts matching keywords.
    L3 FIX: Per-subreddit exception handling — one failure does not stop others.
    L4 FIX: Use 'new' sort for recency, not 'hot'.
    """
    reddit = get_client()
    rows: list[dict] = []

    for sub in CRYPTO_SUBREDDITS:
        try:
            for post in reddit.subreddit(sub).new(limit=limit):
                title_lower = post.title.lower()
                if any(kw.lower() in title_lower for kw in keywords):
                    rows.append({
                        "source": f"r/{sub}",
                        "title": post.title,
                        "text": (post.selftext or "")[:300],
                        "upvotes": post.score,
                        "comments": post.num_comments,
                        "created_at": datetime.fromtimestamp(post.created_utc),
                        "url": f"https://reddit.com{post.permalink}",
                    })
        except Exception as e:
            logger.warning(f"r/{sub} fetch failed: {e}")
            continue  # Do not let one subreddit failure stop the rest

    if not rows:
        logger.info(f"No posts found for keywords: {keywords}")
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    return df.sort_values("created_at", ascending=False).reset_index(drop=True)
