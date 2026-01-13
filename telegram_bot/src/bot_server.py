"""Telegram bot server - main bot handlers."""
import os
import subprocess
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from database import (
    add_incoming_message,
    is_locked,
    init_db
)
from voice_transcription import transcribe_voice
from whitelist import is_whitelisted


# Configuration from environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/root/workspace")
DB_PATH = os.path.join(WORKSPACE_DIR, "telegram_bot", "messages.db")
VOICE_DIR = os.path.join(WORKSPACE_DIR, "telegram_bot", "voice_files")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command.

    Args:
        update: Telegram update
        context: Telegram context
    """
    await update.message.reply_text(
        "Hello! I'm your autonomous agent. Send me a message or voice note and I'll respond."
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command.

    Shows processing lock status and system health.

    Args:
        update: Telegram update
        context: Telegram context
    """
    lock_status = "locked" if is_locked(DB_PATH) else "unlocked"

    status_msg = f"""📊 Agent Status

Processing lock: {lock_status}

The agent is {"currently processing messages" if is_locked(DB_PATH) else "ready to process messages"}.
"""

    await update.message.reply_text(status_msg)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages.

    Args:
        update: Telegram update
        context: Telegram context
    """
    chat_id = update.effective_chat.id

    # Check whitelist
    if not is_whitelisted(chat_id):
        user_id = update.effective_user.id
        username = update.effective_user.username
        # Log the chat_id for the user to add to whitelist
        print(f"UNAUTHORIZED ACCESS - Chat ID: {chat_id}, User ID: {user_id}, Username: @{username}")
        await update.message.reply_text(
            f"Sorry, you are not authorized to use this bot.\n\nYour Chat ID: {chat_id}\n\nAdd this to ALLOWED_CHAT_IDS in .env file."
        )
        return

    # Extract message details
    user_id = update.effective_user.id
    username = update.effective_user.username
    message_id = update.message.message_id
    text = update.message.text

    # Store in database
    add_incoming_message(
        DB_PATH,
        chat_id,
        user_id,
        username,
        message_id,
        text
    )

    # Trigger processing if unlocked
    if not is_locked(DB_PATH):
        trigger_processing()


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming voice messages.

    Downloads voice file, transcribes it, and stores both in database.

    Args:
        update: Telegram update
        context: Telegram context
    """
    chat_id = update.effective_chat.id

    # Check whitelist
    if not is_whitelisted(chat_id):
        user_id = update.effective_user.id
        username = update.effective_user.username
        # Log the chat_id for the user to add to whitelist
        print(f"UNAUTHORIZED ACCESS - Chat ID: {chat_id}, User ID: {user_id}, Username: @{username}")
        await update.message.reply_text(
            f"Sorry, you are not authorized to use this bot.\n\nYour Chat ID: {chat_id}\n\nAdd this to ALLOWED_CHAT_IDS in .env file."
        )
        return

    # Extract message details
    user_id = update.effective_user.id
    username = update.effective_user.username
    message_id = update.message.message_id

    # Download voice file
    voice_file = await update.message.voice.get_file()

    # Ensure voice directory exists
    os.makedirs(VOICE_DIR, exist_ok=True)

    voice_path = os.path.join(VOICE_DIR, f"voice_{message_id}.ogg")
    await voice_file.download_to_drive(voice_path)

    # Transcribe
    result = transcribe_voice(voice_path)

    if result['success']:
        transcription = result['transcription']

        # Store in database with transcription
        add_incoming_message(
            DB_PATH,
            chat_id,
            user_id,
            username,
            message_id,
            None,  # No text for voice
            voice_path,
            transcription
        )

        # Trigger processing if unlocked
        if not is_locked(DB_PATH):
            trigger_processing()

    else:
        # Transcription failed
        await update.message.reply_text(
            f"Sorry, I couldn't transcribe your voice message. Error: {result['error']}"
        )


def trigger_processing():
    """Trigger telegram message processing via subprocess.

    Spawns telegram-process.sh script in background.
    """
    script_path = os.path.join(WORKSPACE_DIR, "scripts", "telegram-process.sh")

    subprocess.Popen(
        [script_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )


def main():
    """Run the Telegram bot."""
    # Initialize database
    init_db(DB_PATH)

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Run bot
    print(f"Bot starting... Database: {DB_PATH}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
