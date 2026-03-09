# Project 3 — Auto-Moderation Bot with AI Scam Detection

> Auto-detects crypto scams in Discord using 3-layer detection: allowlist → pattern matching → Claude AI.

## What It Does
- 3-layer detection funnel: trusted role allowlist → pattern matching → AI (only for ambiguous messages)
- Detects seed phrase requests, fake admins, suspicious domains, wallet addresses
- Auto-deletes HIGH_RISK messages, flags SUSPICIOUS ones for review
- Logs all actions to a dedicated mod channel with embedded details
- Hot-reloads scam patterns hourly without bot restart
- All failure paths default to SUSPICIOUS — never SAFE

## Tech Stack
- Python 3.12
- discord.py 2.7.1
- anthropic 0.80.0 (Claude AI second opinion)
- Deployed on: Railway Hobby ($5/month)

## Setup

1. Install: `cd project3-scam-mod-bot && pip install -r requirements.txt`
2. Configure: `cp .env.example .env` — fill in your keys
3. Start: `python discord_mod.py`

## Architecture
Pattern matching handles ~90% of messages at near-zero cost. AI is only invoked for the ~10% of ambiguous SUSPICIOUS messages. This keeps API costs minimal while maintaining high detection accuracy.
