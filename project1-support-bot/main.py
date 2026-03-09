"""
Main entry point for Project 1 — AI-Powered Support Bot.
Run: python main.py telegram   — starts Telegram bot
Run: python main.py discord    — starts Discord bot
"""
import sys
import asyncio


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("telegram", "discord"):
        print("Usage: python main.py [telegram|discord]")
        sys.exit(1)

    platform = sys.argv[1]

    if platform == "telegram":
        from telegram_bot import main as telegram_main
        asyncio.run(telegram_main())
    else:
        from discord_bot import bot
        from config import DISCORD_TOKEN
        bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
