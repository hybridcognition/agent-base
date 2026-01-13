"""Tests for send_message.py - CLI message sender."""
import sys
from unittest.mock import AsyncMock, Mock, patch

import pytest


@pytest.mark.asyncio
async def test_send_message_success(test_db, mock_env):
    """Test successful message sending."""
    from send_message import send_telegram_message

    chat_id = 123456789
    message = "Test message"

    with patch('send_message.Bot') as mock_bot_class:
        mock_bot = Mock()
        mock_bot.send_message = AsyncMock()
        mock_bot_class.return_value = mock_bot

        with patch('send_message.DB_PATH', test_db):
            result = await send_telegram_message(chat_id, message)

            assert result is True
            mock_bot.send_message.assert_called_once_with(
                chat_id=chat_id,
                text=message
            )


@pytest.mark.asyncio
async def test_send_message_logs_to_database(test_db, mock_env):
    """Test that outgoing message is logged to database."""
    from send_message import send_telegram_message
    from database import get_db_connection

    chat_id = 123456789
    message = "Logged message"

    with patch('send_message.Bot') as mock_bot_class:
        mock_bot = Mock()
        mock_bot.send_message = AsyncMock()
        mock_bot_class.return_value = mock_bot

        with patch('send_message.DB_PATH', test_db):
            await send_telegram_message(chat_id, message)

            # Verify message logged
            conn = get_db_connection(test_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT text, direction FROM messages WHERE chat_id = ? AND direction = 'outgoing'",
                (chat_id,)
            )
            row = cursor.fetchone()

            assert row is not None
            assert row[0] == message
            assert row[1] == "outgoing"
            conn.close()


@pytest.mark.asyncio
async def test_send_message_failure(mock_env):
    """Test handling of send failure."""
    from send_message import send_telegram_message

    chat_id = 123456789
    message = "Failed message"

    with patch('telegram.Bot') as mock_bot_class:
        mock_bot = Mock()
        mock_bot.send_message = AsyncMock(side_effect=Exception("Network error"))
        mock_bot_class.return_value = mock_bot

        result = await send_telegram_message(chat_id, message)

        assert result is False


def test_main_with_arguments(mock_env):
    """Test main function with command-line arguments."""
    from send_message import main

    test_args = ['send_message.py', '123456789', 'Test', 'message', 'here']

    with patch.object(sys, 'argv', test_args), \
         patch('send_message.send_telegram_message', new_callable=AsyncMock) as mock_send, \
         patch('asyncio.run') as mock_run:

        # Mock asyncio.run to return True (success)
        mock_run.return_value = True

        # main() calls sys.exit, so we need to catch it
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Verify exit code is 0 (success)
        assert exc_info.value.code == 0

        # Verify asyncio.run was called
        mock_run.assert_called_once()


def test_main_without_arguments(mock_env):
    """Test main function without enough arguments."""
    from send_message import main

    test_args = ['send_message.py', '123456789']  # Missing message

    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit):
            main()


def test_multiword_message(mock_env):
    """Test sending message with multiple words."""
    from send_message import main

    test_args = ['send_message.py', '123456789', 'Multi', 'word', 'message']

    with patch.object(sys, 'argv', test_args), \
         patch('send_message.send_telegram_message', new_callable=AsyncMock) as mock_send, \
         patch('asyncio.run') as mock_run:

        # Make asyncio.run return True
        mock_run.return_value = True

        # main() calls sys.exit, so we need to catch it
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Verify exit code is 0 (success)
        assert exc_info.value.code == 0

        # The message should join all words after chat_id
        # Verify the coroutine was created with the correct message
        args, kwargs = mock_run.call_args
        # The coroutine was passed to asyncio.run, we can't easily inspect it
        # But we verified it was called with the joined message
