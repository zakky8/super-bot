import discord
from discord.ext import commands
from loguru import logger

from config import DISCORD_TOKEN
from ai_engine import get_ai_response
from rate_limiter import rate_limiter

intents = discord.Intents.default()
intents.message_content = True  # Required in discord.py 2.x

bot = commands.Bot(command_prefix="!", intents=intents)
user_histories: dict[int, list[dict]] = {}


@bot.event
async def on_ready() -> None:
    logger.info(f"Discord bot online as {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_message(message: discord.Message) -> None:
    # Guard: never process bot's own messages
    if message.author.bot:
        return

    user_id = message.author.id

    # L3: Rate limit
    if not rate_limiter.is_allowed(user_id):
        wait = rate_limiter.time_until_reset(user_id)
        await message.channel.send(
            f"⏳ {message.author.mention} — wait {wait}s before sending again.",
            delete_after=10,
        )
        return

    async with message.channel.typing():
        history = user_histories.get(user_id, [])
        response = await get_ai_response(message.content, history)

        if response == "ESCALATE":
            await message.channel.send(
                f"🔔 {message.author.mention} — connecting you to a human moderator."
            )
        else:
            await message.channel.send(response)
            history.append({"role": "user", "content": message.content})
            history.append({"role": "assistant", "content": response})
            user_histories[user_id] = history

    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
