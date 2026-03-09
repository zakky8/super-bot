import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from loguru import logger

# L4 FIX: create once at module level — not inside functions
_vader = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> dict:
    """
    VADER primary analysis.
    L4 FIX: TextBlob only runs when VADER is uncertain (near-neutral).
    This skips TextBlob for ~60% of clearly positive or negative messages.
    """
    if not text or len(str(text).strip()) < 3:
        return {"score": 0.0, "label": "neutral"}

    compound = _vader.polarity_scores(str(text))["compound"]

    # Only run TextBlob when VADER is ambiguous
    if -0.1 <= compound <= 0.1:
        try:
            from textblob import TextBlob  # lazy import — only when needed
            tb = TextBlob(str(text)).sentiment.polarity
            combined = (compound * 0.6) + (tb * 0.4)
        except Exception:
            combined = compound
    else:
        combined = compound

    label = (
        "positive" if combined >= 0.05
        else "negative" if combined <= -0.05
        else "neutral"
    )
    return {"score": round(combined, 4), "label": label}


def analyze_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply sentiment analysis to all rows using vectorized apply."""
    if df.empty:
        return df
    df = df.copy()
    df["full_text"] = (
        df["title"].fillna("") + " " +
        df.get("text", pd.Series("", index=df.index)).fillna("")
    )
    results = df["full_text"].apply(analyze_sentiment)
    df["sentiment_score"] = results.apply(lambda x: x["score"])
    df["sentiment_label"] = results.apply(lambda x: x["label"])
    logger.info(f"Sentiment analyzed: {len(df)} posts")
    return df
