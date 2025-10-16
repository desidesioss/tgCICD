import asyncio
import logging
import os
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message



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
    token = "8100064452:AAH8mS1Jmoa0HlcNQQh9W-g2FKq6SGCvfcU"
    if not token:
        raise RuntimeError(
            "Environment variable BOT_TOKEN is not set. "
            "Create a bot via @BotFather and export BOT_TOKEN before running.",
        )

    logging.basicConfig(level=logging.INFO)

    dp = Dispatcher()
    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_echo, F.text)

    bot = Bot(token=token)
    await dp.start_polling(bot)


def main() -> None:
    """Entry point when running the module as a script."""
    asyncio.run(run())


if __name__ == "__main__":
    main()


# ---------------------- pytest tests below ----------------------

def test_create_echo_reply_returns_same_text() -> None:
    text = "hello world"
    assert create_echo_reply(text) == text


def test_create_echo_reply_handles_empty_input() -> None:
    assert create_echo_reply("") == ""
    assert create_echo_reply(None) == ""
