# Super Bot — Advanced Multi-Platform Bot System

> Production-ready multi-platform bot system for **Telegram** and **Discord** — combining 159 moderation/management commands with **Claude AI** support automation. Both bots share a single Anthropic-powered AI service with FAQ-based answers, prompt-injection protection, conversation memory, and human escalation.

![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue) ![Node.js](https://img.shields.io/badge/Node.js-18+-green) ![Claude AI](https://img.shields.io/badge/Claude-claude--sonnet--4--6-orange)

---

## Repository Structure

```
super-bot/
├── telegram-bot/          # 104-command Telegram bot (Grammy / TypeScript)
├── discord-bot/           # 55-command Discord bot (Discord.js / TypeScript)
├── shared/                # Shared AI service, DB models, Redis utils
├── faq_data.json          # FAQ knowledge base for Claude AI answers
├── docker-compose.yml     # Full stack (bots + Postgres + Redis + Ollama)
└── ecosystem.config.js    # PM2 process config
```

---

## AI System — Anthropic Claude (Integrated)

Both bots use the **same upgraded AI service** in `shared/src/services/ai/AIService.ts`.

| Feature | How it works |
|---------|-------------|
| **Claude AI** | Primary provider via `@anthropic-ai/sdk`. Reads `ANTHROPIC_API_KEY` |
| **FAQ-based answers** | Loads `faq_data.json` and builds a system prompt. AI only answers from the FAQ |
| **Prompt injection guard** | 8 blocked phrases — attempts are logged and replaced with a safe message |
| **Human escalation** | When AI cannot answer it returns `ESCALATE` → bot notifies the moderator |
| **Conversation memory** | Last 10 turns stored in Redis per user (falls back to in-memory) |
| **Rate limiting** | 20 requests per hour per user (Redis-backed) |
| **Ollama fallback** | If Anthropic API fails, auto-falls back to local Ollama model |

### AI Commands

**Telegram:**

| Command | Description |
|---------|-------------|
| `/chat <message>` | Ask the Claude AI anything |
| `/chat clear` | Reset conversation history |
| `/ask <question>` | Alias for `/chat` |
| `/support <issue>` | Escalate directly to a human moderator |
| `/aisetup` | Configure API key, model, test connection, reload FAQ |

**Discord:**

| Command | Description |
|---------|-------------|
| `/chat message:<text>` | Ask the Claude AI |
| `/chat clear:true` | Reset conversation history |

### AI Quick Setup

1. Get your API key at [console.anthropic.com](https://console.anthropic.com/)
2. Add to `.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-...
   ANTHROPIC_MODEL=claude-sonnet-4-6
   BOT_NAME=SupportBot
   HUMAN_MODERATOR_CHAT_ID=<telegram_id>   # optional
   HUMAN_MODERATOR_CHANNEL=<discord_channel_id>  # optional
   ```
3. Edit `faq_data.json` with your Q&A pairs
4. Start the bots — Claude AI is active immediately

---

## Telegram Bot — 104 Commands

Built with **Grammy**. Full MissRose feature parity.

| Module | Commands | Description |
|--------|----------|-------------|
| Moderation | 22 | Ban, kick, mute, warn, purge (silent + timed variants) |
| Admin | 11 | Promote, demote, group config, log channel |
| Anti-Spam | 17 | Locks, flood control, blacklist, CAPTCHA, anti-raid |
| Greetings | 10 | Welcome/goodbye with custom messages and mute-on-join |
| Content | 13 | Notes, filters, rules with media support |
| Federation | 15 | Multi-group cross-ban system |
| Utilities | 11 | Info, stats, connection management |
| AI | 3 | `/chat`, `/ask`, `/support` |
| Fun | 5 | hug, pat, slap, roll, runs |

---

## Discord Bot — 55 Commands

Built with **Discord.js**. Full MEE6 feature parity.

| Module | Commands | Description |
|--------|----------|-------------|
| Moderation | 16 | Ban, kick, timeout, warn, purge, lockdown with log channel |
| Leveling | 12 | XP, ranks, leaderboards, role rewards, multipliers |
| Custom Commands | 5 | User-defined commands |
| Reaction Roles | 4 | Self-assignable roles via emoji |
| Engagement | 7 | Polls, giveaways, reminders, birthdays |
| Social | 4 | Twitch, YouTube, Twitter, Reddit alerts |
| Utilities | 7 | Server/user info, avatar, ping |
| AI | 1 | `/chat` |

---

## Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### Setup

```bash
# Clone and install
git clone https://github.com/zakky8/super-bot.git
cd super-bot

# Install all dependencies
npm run install:all

# Configure environment
cp .env.example .env
# Edit .env — fill ANTHROPIC_API_KEY, BOT tokens, DATABASE_URL, REDIS_URL

# Build
npm run build

# Start (development)
npm run dev:telegram
npm run dev:discord

# Start (production via PM2)
pm2 start ecosystem.config.js
```

### Docker (full stack)

```bash
cp .env.example .env
# Fill in .env values

docker-compose up -d
# Starts: telegram-bot, discord-bot, postgres, redis, ollama
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key — [get one here](https://console.anthropic.com/) |
| `ANTHROPIC_MODEL` | No | Claude model (default: `claude-sonnet-4-6`) |
| `BOT_NAME` | No | AI assistant name in responses (default: `SupportBot`) |
| `TELEGRAM_BOT_TOKEN` | Yes | From [@BotFather](https://t.me/BotFather) |
| `DISCORD_BOT_TOKEN` | Yes | From [Discord Developer Portal](https://discord.com/developers) |
| `DISCORD_CLIENT_ID` | Yes | Discord application client ID |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | No | Redis URL (defaults to in-memory fallback) |
| `HUMAN_MODERATOR_CHAT_ID` | No | Telegram chat ID for escalation alerts |
| `HUMAN_MODERATOR_CHANNEL` | No | Discord channel ID for escalation alerts |
| `OLLAMA_HOST` | No | Ollama host for local AI fallback |

---

## FAQ Knowledge Base

Edit `faq_data.json` to customise what the AI knows:

```json
[
  { "q": "How do I reset my password?", "a": "Click 'Forgot Password' on the login page." },
  { "q": "What are the trading fees?", "a": "0.1% per trade. VIP members get reduced fees." }
]
```

Reload without restarting: `/aisetup faq` (Telegram)

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│               telegram-bot (Grammy)              │
│  104 commands │ /chat /ask /support /aisetup     │
└────────────────────────┬────────────────────────┘
                         │ imports
┌────────────────────────▼────────────────────────┐
│              shared / AIService                  │
│  Anthropic SDK • FAQ loader • Injection guard    │
│  Escalation • Redis memory • Ollama fallback     │
└────────────────────────┬────────────────────────┘
                         │ imports
┌────────────────────────▼────────────────────────┐
│             discord-bot (Discord.js)             │
│  55 commands │ /chat (slash command)             │
└─────────────────────────────────────────────────┘
```

---

## Related Repositories

| Repo | Description |
|------|-------------|
| [zakky8/Auto-Moderation](https://github.com/zakky8/Auto-Moderation) | Standalone AI scam detection moderation bot |
| [zakky8/Support-Ticket-Classifier](https://github.com/zakky8/Support-Ticket-Classifier) | ML-powered ticket routing dashboard |
| [zakky8/Crypto-Sentiment-Tracker](https://github.com/zakky8/Crypto-Sentiment-Tracker) | Real-time Reddit + price sentiment tracker |

---

## License

MIT
