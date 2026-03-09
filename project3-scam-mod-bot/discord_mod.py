import discord
from discord.ext import commands, tasks
from loguru import logger

from config import DISCORD_TOKEN, LOG_CHANNEL_ID  # B22 FIX: through config, not os.getenv directly
from pattern_detector import detect_scam, RiskLevel, reload_patterns
from ai_classifier import ai_classify_message

intents = discord.Intents.default()
intents.message_content = True  # Required in discord.py 2.x

bot = commands.Bot(command_prefix="!", intents=intents)

MODERATED_CHANNELS: list[int] = []  # Empty = all channels


@bot.event
async def on_ready() -> None:
    logger.info(f"Mod bot online as {bot.user}")
    hourly_pattern_refresh.start()


# CORRECT ORDER: define the @tasks.loop function FIRST,
# then attach the .error handler — Python resolves names top-to-bottom
@tasks.loop(hours=1)
async def hourly_pattern_refresh() -> None:
    """L5: Reload patterns every hour without restarting."""
    try:
        reload_patterns()
    except Exception as e:
        logger.error(f"reload_patterns() failed: {e}")


@hourly_pattern_refresh.error
async def hourly_pattern_refresh_error(error: Exception) -> None:
    # B23 FIX: without this, any unhandled exception silently kills the loop forever
    logger.error(f"Pattern refresh loop error: {error} — loop will retry next hour")


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    if MODERATED_CHANNELS and message.channel.id not in MODERATED_CHANNELS:
        await bot.process_commands(message)
        return

    role_ids = [r.id for r in getattr(message.author, "roles", [])]
    result = detect_scam(message.content, role_ids)

    if result.risk_level == RiskLevel.HIGH_RISK:
        await _delete_and_warn(message)
        await _log(message, result.reasons, "AUTO_DELETED")

    elif result.risk_level == RiskLevel.SUSPICIOUS:
        ai_verdict = await ai_classify_message(message.content)
        if ai_verdict == RiskLevel.HIGH_RISK:
            await _delete_and_warn(message)
            await _log(message, result.reasons, "AI_DELETED")
        else:
            await _log(message, result.reasons, "FLAGGED_FOR_REVIEW")

    await bot.process_commands(message)


async def _delete_and_warn(message: discord.Message) -> None:
    try:
        await message.delete()
    except discord.Forbidden:
        logger.warning(f"No permission to delete in #{message.channel.name}")
    await message.channel.send(
        f"⚠️ {message.author.mention} — Message removed for violating safety rules.",
        delete_after=10,
    )


async def _log(
    message: discord.Message, reasons: list[str], action: str
) -> None:
    logger.info(f"Mod action={action} user={message.author} reasons={reasons}")
    if not LOG_CHANNEL_ID:
        return
    ch = bot.get_channel(LOG_CHANNEL_ID)
    if not ch:
        return
    embed = discord.Embed(
        title=f"Mod Action: {action}",
        color=discord.Color.red() if "DELETED" in action else discord.Color.orange(),
    )
    embed.add_field(name="User", value=f"{message.author} ({message.author.id})")
    embed.add_field(name="Channel", value=message.channel.mention)
    embed.add_field(name="Reasons", value="\n".join(reasons) or "None", inline=False)
    embed.add_field(name="Content", value=message.content[:200], inline=False)
    await ch.send(embed=embed)


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
