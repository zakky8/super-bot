# AI-Powered Crypto Bot Suite

> Production-ready Python bot system with Claude AI integration. Four independent projects covering support automation, scam detection, ticket classification, and sentiment tracking.

**Python 3.12 · anthropic 0.80.0 · aiogram 3.26.0 · discord.py 2.7.1 · streamlit 1.55.0**

---

## Projects

| # | Project | Stack | Deploy |
|---|---------|-------|--------|
| 1 | [AI Support Bot](#project-1--ai-support-bot) | aiogram + discord.py + Claude AI | Railway |
| 3 | [Scam Mod Bot](#project-3--scam-mod-bot) | discord.py + Claude AI | Railway |
| 4 | [Ticket Classifier](#project-4--ticket-classifier) | Streamlit + sentence-transformers | Streamlit Cloud |
| 5 | [Sentiment Tracker](#project-5--sentiment-tracker) | Streamlit + PRAW + CoinGecko | Streamlit Cloud |

---

## Project 1 — AI Support Bot

Dual-platform (Telegram + Discord) support bot powered by Claude AI. Answers FAQ questions, rate-limits users (5 msg/60s), blocks prompt injection, escalates unresolvable tickets to human agents.

**Tech:** aiogram 3.26.0 · discord.py 2.7.1 · anthropic 0.80.0

```bash
cd project1-support-bot
pip install -r requirements.txt
cp .env.example .env   # fill in TELEGRAM_TOKEN, DISCORD_TOKEN, ANTHROPIC_API_KEY
python main.py telegram    # or: python main.py discord
```

**Key fixes applied:** aiogram DefaultBotProperties (B4), singleton Anthropic client (B8), history trimming (B9), prompt injection sanitization (B6), per-user rate limiter (B7), graceful SIGTERM shutdown (B13).

---

## Project 3 — Scam Mod Bot

Discord auto-moderator with 3-layer scam detection: trusted role allowlist → pattern matching → Claude AI (only for ambiguous messages). Auto-deletes high-risk messages. Logs all actions with embeds.

**Tech:** discord.py 2.7.1 · anthropic 0.80.0

```bash
cd project3-scam-mod-bot
pip install -r requirements.txt
cp .env.example .env   # fill in DISCORD_TOKEN, ANTHROPIC_API_KEY, LOG_CHANNEL_ID
python discord_mod.py
```

**Key fixes applied:** guarded JSON load with fallback (B3), pre-compiled regex (B11), LOG_CHANNEL_ID through config (B22), safe int conversion (B20), tasks.loop error handler (B23).

---

## Project 4 — Ticket Classifier

Classifies support tickets into 8 categories with priority scoring. Interactive Streamlit dashboard with suggested responses and confidence display.

**Tech:** sentence-transformers 5.2.3 · scikit-learn 1.8.0 · streamlit 1.55.0

```bash
cd project4-ticket-classifier
pip install -r requirements.txt
python setup.py            # download NLTK data (once)
python train_model.py      # train and save model (once)
streamlit run app.py
```

**Key fixes applied:** `convert_to_numpy=True` for sentence-transformers 5.x (B12), `punkt_tab` for NLTK 3.9+ (B15), `@st.cache_data` replacing deprecated `@st.cache` (B18), models/ excluded from git (B17).

---

## Project 5 — Sentiment Tracker

Live crypto sentiment dashboard. Scrapes 6 Reddit crypto subreddits, analyzes with VADER + TextBlob, displays live CoinGecko prices. 1-hour cache prevents API rate limiting.

**Tech:** praw 7.7.1 · vaderSentiment 3.3.2 · textblob 0.18.0 · streamlit 1.55.0 · plotly 5.24.1

```bash
cd project5-sentiment-tracker
pip install -r requirements.txt
python setup.py            # download NLTK data (once)
cp .env.example .env       # fill in Reddit API credentials
streamlit run dashboard.py
```

**Key fixes applied:** CoinGecko 429 retry with backoff (B14), `punkt_tab` for NLTK 3.9+ (B15), `@st.cache_data` (B18), VADER module-level singleton (L4), TextBlob lazy-loaded only for near-neutral scores.

---

## Deployment

| Platform | Use For | Cost |
|----------|---------|------|
| Railway Hobby | Bots (Projects 1, 3) — must stay always-on | $5/month |
| Streamlit Cloud | Dashboards (Projects 4, 5) | Free |

## Library Versions (Verified March 2026)

| Library | Version | Notes |
|---------|---------|-------|
| aiogram | 3.26.0 | Use `DefaultBotProperties` — `parse_mode` removed from `Bot()` in 3.15 |
| discord.py | 2.7.1 | `intents.message_content = True` required |
| anthropic | 0.80.0 | Model: `claude-sonnet-4-6` |
| sentence-transformers | 5.2.3 | Pass `convert_to_numpy=True` explicitly |
| scikit-learn | 1.8.0 | Requires Python 3.10+ |
| streamlit | 1.55.0 | Use `@st.cache_data`, not `@st.cache` |
| praw | 7.7.1 | Twitter/X API dead since 2023 — use Reddit |
| nltk | 3.9.1 | Download `punkt_tab`, not `punkt` |

## Security

- Per-user rate limiting on all bots
- Prompt injection sanitization before every AI call
- All AI/network failure paths default to SUSPICIOUS (never SAFE) in scam bot
- No secrets committed — `.env.example` provided in each project
- `models/` excluded from git in `.gitignore`

## License

MIT License
