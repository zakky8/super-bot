import asyncio
import signal
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties  # Required since 3.15.0
from aiogram.enums import ParseMode                       # Moved to aiogram.enums
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from loguru import logger

from config import TELEGRAM_TOKEN, HUMAN_MODERATOR_CHAT_ID
from ai_engine import get_ai_response
from rate_limiter import rate_limiter

# B4 FIX CONFIRMED: DefaultBotProperties is the correct pattern since aiogram 3.15
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

user_histories: dict[int, list[dict]] = {}


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_histories[message.from_user.id] = []
    await message.answer(
        "👋 Hello! I'm your support assistant.\n"
        "Ask me anything. Type /clear to reset the conversation."
    )


@dp.message(Command("clear"))
async def cmd_clear(message: Message) -> None:
    user_histories[message.from_user.id] = []
    await message.answer("✅ Conversation cleared. Starting fresh.")


@dp.message(F.text)
async def handle_text(message: Message) -> None:
    user_id = message.from_user.id

    # L3: Per-user rate limit
    if not rate_limiter.is_allowed(user_id):
        wait = rate_limiter.time_until_reset(user_id)
        await message.answer(f"⏳ Too many messages. Please wait {wait}s.")
        return

    history = user_histories.get(user_id, [])
    await bot.send_chat_action(message.chat.id, "typing")

    response = await get_ai_response(message.text, history)

    if response == "ESCALATE":
        await message.answer(
            "🔔 Connecting you to a human support agent. Please wait."
        )
        await _notify_human(user_id, message.text)
    else:
        await message.answer(response)
        history.append({"role": "user", "content": message.text})
        history.append({"role": "assistant", "content": response})
        user_histories[user_id] = history


async def _notify_human(user_id: int, text: str) -> None:
    if not HUMAN_MODERATOR_CHAT_ID:
        logger.warning("HUMAN_MODERATOR_CHAT_ID not set — escalation not sent")
        return
    try:
        await bot.send_message(
            int(HUMAN_MODERATOR_CHAT_ID),
            f"⚠️ <b>ESCALATION NEEDED</b>\n"
            f"User: <code>{user_id}</code>\n"
            f"Message: {text[:300]}",
        )
    except Exception as e:
        logger.error(f"Escalation notification failed: {e}")


async def main() -> None:
    # L5 FIX: graceful shutdown on SIGTERM / SIGINT
    # B19 FIX: use get_running_loop() inside async context (Python 3.10+)
    loop = asyncio.get_running_loop()

    async def _shutdown() -> None:
        logger.info("Shutting down Telegram bot...")
        await dp.stop_polling()
        await bot.session.close()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown()))

    logger.info("Telegram bot starting (polling mode)...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
