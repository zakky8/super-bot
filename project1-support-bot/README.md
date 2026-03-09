# Project 1 — AI-Powered Discord + Telegram Support Bot

> Dual-platform support bot powered by Claude AI. Handles customer queries using FAQ data, rate-limits users, sanitizes inputs, and escalates to human agents when needed.

## What It Does
- Answers support questions using Claude AI (claude-sonnet-4-6) + FAQ database
- Runs on both Telegram (aiogram 3.26.0) and Discord (discord.py 2.7.1)
- Rate-limits users (5 messages/60s) to protect API budget
- Blocks prompt injection attacks
- Escalates unresolvable tickets to human moderators
- Graceful shutdown with SIGTERM handler (Railway-compatible)

## Tech Stack
- Python 3.12
- aiogram 3.26.0 (Telegram)
- discord.py 2.7.1 (Discord)
- anthropic 0.80.0 (Claude AI)
- Deployed on: Railway Hobby ($5/month)

## Setup

1. Clone: `git clone https://github.com/zakky8/super-bot`
2. Install: `cd project1-support-bot && pip install -r requirements.txt`
3. Configure: `cp .env.example .env` — fill in your keys
4. Start Telegram: `python main.py telegram`
5. Start Discord: `python main.py discord`

## Architecture
Single `ai_engine.py` serves both platforms. Platform files only handle events. Singleton Anthropic client. History trimmed to last 10 turns to prevent token overflow.
