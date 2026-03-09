import streamlit as st
import plotly.express as px
import pandas as pd

from reddit_scraper import fetch_posts
from sentiment_analyzer import analyze_dataframe
from price_fetcher import get_prices
from config import COIN_IDS

st.set_page_config(
    page_title="Crypto Sentiment Tracker",
    page_icon="📈",
    layout="wide",
)
st.title("📈 Crypto Sentiment Tracker")
st.caption("Data: Reddit (live) + CoinGecko (live) | Cache: 1 hour")

with st.sidebar:
    st.subheader("⚙️ Settings")
    coins = st.multiselect(
        "Track coins:", list(COIN_IDS.keys()), default=["BTC", "ETH"]
    )
    limit = st.slider("Posts per subreddit", 10, 100, 50)
    if st.button("🔄 Force Refresh"):
        st.cache_data.clear()
        st.rerun()

# B18 FIX: @st.cache_data with TTL — prevents CoinGecko rate limit exhaustion
@st.cache_data(ttl=3600, show_spinner=False)
def load_data(coins_key: tuple, post_limit: int):
    coin_list = list(coins_key)
    df = fetch_posts(coin_list, post_limit)
    if not df.empty:
        df = analyze_dataframe(df)
    prices = get_prices(coin_list)
    return df, prices


if not coins:
    st.warning("Select at least one coin in the sidebar.")
    st.stop()

with st.spinner("Loading live data..."):
    df, prices = load_data(tuple(coins), limit)

# Price metrics
st.subheader("💰 Current Prices")
cols = st.columns(len(coins))
for i, coin in enumerate(coins):
    data = prices.get(COIN_IDS.get(coin, ""), {})
    price = data.get("usd", 0)
    change = data.get("usd_24h_change", 0)
    with cols[i]:
        st.metric(
            coin,
            f"${price:,.2f}" if price else "N/A",
            delta=f"{change:+.2f}%" if change else None,
        )

st.divider()

if df.empty:
    st.info("No posts found. Try different coins or increase the post limit.")
    st.stop()

c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("🎭 Sentiment Split")
    counts = df["sentiment_label"].value_counts()
    fig = px.pie(
        values=counts.values,
        names=counts.index,
        color=counts.index,
        color_discrete_map={
            "positive": "#00CC96",
            "neutral": "#636EFA",
            "negative": "#EF553B",
        },
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("📊 Sentiment Over Time")
    df["hour"] = pd.to_datetime(df["created_at"]).dt.floor("h")
    hourly = df.groupby("hour")["sentiment_score"].mean().reset_index()
    fig2 = px.line(
        hourly, x="hour", y="sentiment_score",
        labels={"sentiment_score": "Avg Sentiment", "hour": "Time"},
    )
    fig2.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig2.add_hline(y=0.05, line_dash="dot", line_color="green", opacity=0.3)
    fig2.add_hline(y=-0.05, line_dash="dot", line_color="red", opacity=0.3)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("📰 Recent Posts")
show = df[["source", "title", "sentiment_label", "sentiment_score", "upvotes"]].head(25).copy()
show.columns = ["Source", "Title", "Sentiment", "Score", "Upvotes"]
st.dataframe(show, use_container_width=True)
