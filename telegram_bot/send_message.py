"""CLI utility for sending Telegram messages.

Usage: python send_message.py <chat_id> <message text>
"""
import asyncio
import os
import sys
from pathlib import Path

from telegram import Bot

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import add_outgoing_message


# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/root/workspace")
DB_PATH = os.path.join(WORKSPACE_DIR, "telegram_bot", "messages.db")


async def send_telegram_message(chat_id: int, message: str) -> bool:
    """Send message via Telegram and log to database.

    Args:
        chat_id: Telegram chat ID
        message: Message text to send

    Returns:
        True if successful, False otherwise
    """
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=chat_id, text=message)

        # Log to database
        add_outgoing_message(DB_PATH, chat_id, message)

        return True

    except Exception as e:
        print(f"Error sending message: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point for CLI."""
    if len(sys.argv) < 3:
        print("Usage: python send_message.py <chat_id> <message text>", file=sys.stderr)
        sys.exit(1)

    chat_id = int(sys.argv[1])
    message = " ".join(sys.argv[2:])

    success = asyncio.run(send_telegram_message(chat_id, message))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
