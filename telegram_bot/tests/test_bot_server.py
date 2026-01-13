"""
Tests for bot_server.py module.
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from src import database as db
from src import bot_server


def create_mock_update(message_text="Test message", chat_id=123456789,
                       user_id=123456789, username="test_user",
                       message_id=1000):
    """Helper to create a mock Telegram Update object."""
    update = MagicMock()
    update.effective_chat.id = chat_id
    update.effective_user.id = user_id
    update.effective_user.username = username
    update.message.text = message_text
    update.message.message_id = message_id
    update.message.reply_text = AsyncMock()
    return update


@pytest.mark.asyncio
async def test_start_command(test_db):
    """Test /start command handler."""
    update = create_mock_update()
    context = MagicMock()

    await bot_server.start_command(update, context)

    update.message.reply_text.assert_called_once()
    reply_text = update.message.reply_text.call_args[0][0]
    assert "Claude Bot is online" in reply_text
    assert "autonomous agent" in reply_text


@pytest.mark.asyncio
async def test_status_command_available(test_db):
    """Test /status command when bot is available."""
    update = create_mock_update()
    context = MagicMock()

    await bot_server.status_command(update, context)

    update.message.reply_text.assert_called_once()
    reply_text = update.message.reply_text.call_args[0][0]
    assert "Bot Status" in reply_text
    assert "IDLE" in reply_text
    assert "Unprocessed messages: 0" in reply_text


@pytest.mark.asyncio
async def test_status_command_busy(test_db):
    """Test /status command when bot has active sessions."""
    update = create_mock_update()
    context = MagicMock()

    # Create an active session
    session_id = "chat_123456789"
    chat_id = 123456789
    session = db.get_or_create_session(session_id, chat_id)

    # Add a message to get a valid message_id
    message_id = db.add_incoming_message(
        chat_id=chat_id,
        user_id=123456789,
        username="test_user",
        message_text="Test message",
        telegram_message_id=1000,
        session_id=session_id
    )

    db.acquire_session_lock(session_id, process_id=99999, message_id=message_id)

    await bot_server.status_command(update, context)

    update.message.reply_text.assert_called_once()
    reply_text = update.message.reply_text.call_args[0][0]
    assert "Bot Status" in reply_text
    assert "Active Sessions" in reply_text
    assert "99999" in reply_text

    # Cleanup
    db.release_session_lock(session_id)


@pytest.mark.asyncio
async def test_handle_message_stores_in_database(test_db):
    """Test that handle_message stores the message in database."""
    chat_id = 987654321
    user_id = 111222333
    username = "john_doe"
    message_text = "Hello Claude!"
    telegram_message_id = 7777

    # Add user to whitelist
    os.environ['ALLOWED_USER_IDS'] = str(user_id)
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
    from src import whitelist
    whitelist.reload_whitelist()

    update = create_mock_update(
        message_text=message_text,
        chat_id=chat_id,
        user_id=user_id,
        username=username,
        message_id=telegram_message_id
    )
    context = MagicMock()

    with patch('src.bot_server.trigger_session_processing'):
        await bot_server.handle_message(update, context)

    # Verify message was stored
    unprocessed = db.get_unprocessed_messages()
    assert len(unprocessed) > 0

    stored_msg = unprocessed[-1]  # Get last message
    assert stored_msg['chat_id'] == chat_id
    assert stored_msg['user_id'] == user_id
    assert stored_msg['username'] == username
    assert stored_msg['message_text'] == message_text
    assert stored_msg['telegram_message_id'] == telegram_message_id
    assert stored_msg['direction'] == 'incoming'
    assert stored_msg['processed'] == 0


@pytest.mark.asyncio
async def test_handle_message_starts_new_session(test_db):
    """Test handle_message starts a new session when none is active."""
    chat_id = 123456789
    user_id = 123456789

    # Add user to whitelist
    os.environ['ALLOWED_USER_IDS'] = str(user_id)
    from src import whitelist
    whitelist.reload_whitelist()

    update = create_mock_update(chat_id=chat_id, user_id=user_id)
    context = MagicMock()

    with patch('src.bot_server.trigger_session_processing') as mock_trigger:
        await bot_server.handle_message(update, context)

        # Should have triggered session processing
        mock_trigger.assert_called_once()
        # Check it was called with session_id and chat_id
        call_args = mock_trigger.call_args[0]
        assert call_args[0] == f"chat_{chat_id}"
        assert call_args[1] == chat_id

        # Should have sent "Starting conversation" message
        assert update.message.reply_text.call_count >= 1
        call_args = [call[0][0] for call in update.message.reply_text.call_args_list]
        assert any("Starting conversation" in arg for arg in call_args)


@pytest.mark.asyncio
async def test_handle_message_when_session_active(test_db):
    """Test handle_message when session is already active - should queue message."""
    chat_id = 123456789
    user_id = 123456789
    session_id = f"chat_{chat_id}"

    # Add user to whitelist
    os.environ['ALLOWED_USER_IDS'] = str(user_id)
    from src import whitelist
    whitelist.reload_whitelist()

    # Create and lock the session
    session = db.get_or_create_session(session_id, chat_id)

    # Add a message to get a valid message_id
    message_id = db.add_incoming_message(
        chat_id=chat_id,
        user_id=user_id,
        username="test_user",
        message_text="First message",
        telegram_message_id=999,
        session_id=session_id
    )

    db.acquire_session_lock(session_id, process_id=88888, message_id=message_id)

    update = create_mock_update(chat_id=chat_id, user_id=user_id)
    context = MagicMock()

    with patch('src.bot_server.trigger_session_processing') as mock_trigger:
        await bot_server.handle_message(update, context)

        # Should NOT have triggered processing (session already active)
        mock_trigger.assert_not_called()

        # Should have sent "Added to ongoing conversation" message
        update.message.reply_text.assert_called_once()
        reply_text = update.message.reply_text.call_args[0][0]
        assert "ongoing conversation" in reply_text

    # Cleanup
    db.release_session_lock(session_id)


@pytest.mark.asyncio
async def test_handle_voice_success(test_db):
    """Test successful voice message handling."""
    chat_id = 555666777
    user_id = 111222333
    username = "voice_user"
    telegram_message_id = 8888

    # Add user to whitelist
    os.environ['ALLOWED_USER_IDS'] = str(user_id)
    from src import whitelist
    whitelist.reload_whitelist()

    # Create mock update for voice message
    update = MagicMock()
    update.effective_chat.id = chat_id
    update.effective_user.id = user_id
    update.effective_user.username = username
    update.message.message_id = telegram_message_id
    update.message.reply_text = AsyncMock()

    # Mock voice file
    mock_voice = MagicMock()
    mock_file = AsyncMock()
    mock_file.download_to_drive = AsyncMock()
    mock_voice.get_file = AsyncMock(return_value=mock_file)
    update.message.voice = mock_voice

    context = MagicMock()

    # Mock transcription result
    transcription_result = {
        'success': True,
        'text': 'This is the transcribed text'
    }

    with patch('src.bot_server.voice_transcription.transcribe_voice_message', return_value=transcription_result):
        with patch('src.bot_server.trigger_session_processing'):
            await bot_server.handle_voice(update, context)

            # Verify file download was attempted
            mock_voice.get_file.assert_called_once()
            mock_file.download_to_drive.assert_called_once()

            # Verify message was stored with transcription
            unprocessed = db.get_unprocessed_messages()
            assert len(unprocessed) > 0

            stored_msg = unprocessed[-1]
            assert stored_msg['chat_id'] == chat_id
            assert stored_msg['message_text'] == 'This is the transcribed text'
            assert stored_msg['voice_transcription'] == 'This is the transcribed text'
            assert stored_msg['voice_file_path'] is not None

            # Verify user was sent transcription
            calls = update.message.reply_text.call_args_list
            transcription_sent = any('Transcription:' in str(call) for call in calls)
            assert transcription_sent


@pytest.mark.asyncio
async def test_handle_voice_transcription_failure(test_db):
    """Test voice message handling when transcription fails."""
    user_id = 456

    # Add user to whitelist
    os.environ['ALLOWED_USER_IDS'] = str(user_id)
    from src import whitelist
    whitelist.reload_whitelist()

    update = MagicMock()
    update.effective_chat.id = 123
    update.effective_user.id = user_id
    update.effective_user.username = "test_user"
    update.message.message_id = 789
    update.message.reply_text = AsyncMock()

    mock_voice = MagicMock()
    mock_file = AsyncMock()
    mock_file.download_to_drive = AsyncMock()
    mock_voice.get_file = AsyncMock(return_value=mock_file)
    update.message.voice = mock_voice

    context = MagicMock()

    # Mock failed transcription
    transcription_result = {
        'success': False,
        'error': 'Failed to load audio file'
    }

    with patch('src.bot_server.voice_transcription.transcribe_voice_message', return_value=transcription_result):
        await bot_server.handle_voice(update, context)

        # Verify error message was sent
        calls = update.message.reply_text.call_args_list
        error_sent = any("couldn't transcribe" in str(call) for call in calls)
        assert error_sent


@pytest.mark.asyncio
async def test_handle_voice_exception(test_db):
    """Test voice message handling when an exception occurs."""
    user_id = 456

    # Add user to whitelist
    os.environ['ALLOWED_USER_IDS'] = str(user_id)
    from src import whitelist
    whitelist.reload_whitelist()

    update = MagicMock()
    update.effective_chat.id = 123
    update.effective_user.id = user_id
    update.effective_user.username = "test_user"
    update.message.message_id = 789
    update.message.reply_text = AsyncMock()

    mock_voice = MagicMock()
    mock_voice.get_file = AsyncMock(side_effect=Exception("Network error"))
    update.message.voice = mock_voice

    context = MagicMock()

    await bot_server.handle_voice(update, context)

    # Verify error message was sent
    update.message.reply_text.assert_called()
    calls = update.message.reply_text.call_args_list
    error_sent = any("error occurred" in str(call) for call in calls)
    assert error_sent


@pytest.mark.unit
def test_trigger_session_processing(test_db):
    """Test trigger_session_processing function."""
    session_id = "chat_123"
    chat_id = 123

    with patch('subprocess.Popen') as mock_subprocess:
        bot_server.trigger_session_processing(session_id, chat_id)

        # Verify subprocess.Popen was called
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args

        # Check that it's calling the telegram-session.sh script
        assert 'telegram-session.sh' in str(call_args)
        assert session_id in str(call_args)
        assert str(chat_id) in str(call_args)


@pytest.mark.unit
def test_trigger_session_processing_exception(test_db):
    """Test trigger_session_processing when subprocess fails."""
    session_id = "chat_123"
    chat_id = 123

    # Create the session first
    db.get_or_create_session(session_id, chat_id)

    with patch('subprocess.Popen', side_effect=Exception("Command failed")):
        # Should not raise exception, just log error
        bot_server.trigger_session_processing(session_id, chat_id)

        # Verify session lock was released after failure
        session = db.get_session(session_id)
        assert not session['locked']


@pytest.mark.asyncio
async def test_send_telegram_message_success(test_db):
    """Test send_telegram_message function."""
    chat_id = 999888777
    message = "Test outgoing message"

    with patch('src.bot_server.Application') as MockApp:
        mock_app_instance = MagicMock()
        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock()
        mock_app_instance.bot = mock_bot

        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app_instance
        MockApp.builder.return_value = mock_builder

        result = await bot_server.send_telegram_message(chat_id, message)

        assert result is True
        mock_bot.send_message.assert_called_once_with(chat_id=chat_id, text=message)

        # Verify message was logged to database
        recent = db.get_recent_messages(limit=1)
        assert len(recent) == 1
        assert recent[0]['chat_id'] == chat_id
        assert recent[0]['message_text'] == message
        assert recent[0]['direction'] == 'outgoing'


@pytest.mark.asyncio
async def test_send_telegram_message_failure(test_db):
    """Test send_telegram_message when sending fails."""
    chat_id = 111222333
    message = "Test message"

    with patch('src.bot_server.Application') as MockApp:
        mock_app_instance = MagicMock()
        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock(side_effect=Exception("Network error"))
        mock_app_instance.bot = mock_bot

        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app_instance
        MockApp.builder.return_value = mock_builder

        result = await bot_server.send_telegram_message(chat_id, message)

        assert result is False
