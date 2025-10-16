import asyncio
import logging
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import load_settings

def create_echo_reply(text: Optional[str]) -> str:
    """Return the same text that was received, defaulting to empty string."""
    return text or ""


async def handle_start(message: Message) -> None:
    """Send a friendly greeting when /start is issued."""
    await message.answer(
        "Привет! Я эхо-бот. Пришли мне сообщение, и я повторю его.",
    )


async def handle_echo(message: Message) -> None:
    """Echo back whatever text message was sent by the user."""
    await message.answer(create_echo_reply(message.text))


async def run() -> None:
    """Configure dispatcher and start polling Telegram for updates."""
    settings = load_settings()

    logging.basicConfig(level=logging.INFO)

    dp = Dispatcher()
    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_echo, F.text)

    bot = Bot(token=settings.bot_token)
    await dp.start_polling(bot)


def main() -> None:
    """Entry point when running the module as a script."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
