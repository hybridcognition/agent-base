"""Tests for bot_server.py - Telegram bot handlers."""
from unittest.mock import AsyncMock, Mock, patch

import pytest


@pytest.mark.asyncio
async def test_start_command():
    """Test /start command sends welcome message."""
    from bot_server import start_command

    update = Mock()
    update.message.reply_text = AsyncMock()
    context = Mock()

    await start_command(update, context)

    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args[0][0]
    assert "autonomous agent" in call_args.lower()


@pytest.mark.asyncio
async def test_status_command(test_db, mock_env):
    """Test /status command shows system status."""
    from bot_server import status_command

    update = Mock()
    update.message.reply_text = AsyncMock()
    context = Mock()

    with patch('bot_server.DB_PATH', test_db):
        await status_command(update, context)

    update.message.reply_text.assert_called_once()
    call_args = update.message.reply_text.call_args[0][0]
    assert "status" in call_args.lower() or "lock" in call_args.lower()


@pytest.mark.asyncio
async def test_handle_message_whitelist_allowed(test_db, mock_env):
    """Test handling message from whitelisted user."""
    from bot_server import handle_message

    update = Mock()
    update.effective_chat.id = 123456789  # In whitelist
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.message.message_id = 12345
    update.message.text = "Hello agent"
    update.message.reply_text = AsyncMock()

    context = Mock()

    with patch('bot_server.DB_PATH', test_db), \
         patch('bot_server.is_whitelisted', return_value=True):

        await handle_message(update, context)

        # Should not send rejection message
        update.message.reply_text.assert_not_called()


@pytest.mark.asyncio
async def test_handle_message_whitelist_denied(mock_env):
    """Test handling message from non-whitelisted user."""
    from bot_server import handle_message

    update = Mock()
    update.effective_chat.id = 999999999  # Not in whitelist
    update.message.reply_text = AsyncMock()

    context = Mock()

    with patch('bot_server.is_whitelisted', return_value=False):
        await handle_message(update, context)

        # Should send rejection message
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "not authorized" in call_args.lower() or "not allowed" in call_args.lower()


@pytest.mark.asyncio
async def test_handle_message_stores_in_db(test_db, mock_env):
    """Test that message is stored in database."""
    from bot_server import handle_message
    from database import get_unprocessed_messages

    update = Mock()
    update.effective_chat.id = 123456789
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.message.message_id = 12345
    update.message.text = "Store this message"
    update.message.reply_text = AsyncMock()

    context = Mock()

    with patch('bot_server.DB_PATH', test_db), \
         patch('bot_server.is_whitelisted', return_value=True), \
         patch('bot_server.trigger_processing'):

        await handle_message(update, context)

        # Verify message in database
        messages = get_unprocessed_messages(test_db)
        assert len(messages) == 1
        assert messages[0]['text'] == "Store this message"


@pytest.mark.asyncio
async def test_handle_message_triggers_processing(test_db, mock_env):
    """Test that processing is triggered when lock available."""
    from bot_server import handle_message

    update = Mock()
    update.effective_chat.id = 123456789
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.message.message_id = 12345
    update.message.text = "Trigger processing"
    update.message.reply_text = AsyncMock()

    context = Mock()

    with patch('bot_server.DB_PATH', test_db), \
         patch('bot_server.is_whitelisted', return_value=True), \
         patch('bot_server.is_locked', return_value=False), \
         patch('bot_server.trigger_processing') as mock_trigger:

        await handle_message(update, context)

        # Verify processing triggered
        mock_trigger.assert_called_once()


@pytest.mark.asyncio
async def test_handle_message_skips_trigger_when_locked(test_db, mock_env):
    """Test that processing is not triggered when locked."""
    from bot_server import handle_message

    update = Mock()
    update.effective_chat.id = 123456789
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.message.message_id = 12345
    update.message.text = "Message while locked"
    update.message.reply_text = AsyncMock()

    context = Mock()

    with patch('bot_server.DB_PATH', test_db), \
         patch('bot_server.is_whitelisted', return_value=True), \
         patch('bot_server.is_locked', return_value=True), \
         patch('bot_server.trigger_processing') as mock_trigger:

        await handle_message(update, context)

        # Verify processing NOT triggered
        mock_trigger.assert_not_called()


@pytest.mark.asyncio
async def test_handle_voice_downloads_file(test_db, mock_env):
    """Test that voice message is downloaded."""
    from bot_server import handle_voice

    update = Mock()
    update.effective_chat.id = 123456789
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.message.message_id = 12345
    update.message.reply_text = AsyncMock()
    update.message.voice.get_file = AsyncMock()

    mock_file = Mock()
    mock_file.download_to_drive = AsyncMock()
    update.message.voice.get_file.return_value = mock_file

    context = Mock()

    with patch('bot_server.DB_PATH', test_db), \
         patch('bot_server.is_whitelisted', return_value=True), \
         patch('bot_server.transcribe_voice', return_value={'success': True, 'transcription': 'Test'}), \
         patch('bot_server.trigger_processing'):

        await handle_voice(update, context)

        # Verify file downloaded
        update.message.voice.get_file.assert_called_once()
        mock_file.download_to_drive.assert_called_once()


@pytest.mark.asyncio
async def test_handle_voice_transcribes(test_db, mock_env):
    """Test that voice message is transcribed."""
    from bot_server import handle_voice

    update = Mock()
    update.effective_chat.id = 123456789
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.message.message_id = 12345
    update.message.reply_text = AsyncMock()
    update.message.voice.get_file = AsyncMock()

    mock_file = Mock()
    mock_file.download_to_drive = AsyncMock()
    update.message.voice.get_file.return_value = mock_file

    context = Mock()

    with patch('bot_server.DB_PATH', test_db), \
         patch('bot_server.is_whitelisted', return_value=True), \
         patch('bot_server.transcribe_voice') as mock_transcribe, \
         patch('bot_server.trigger_processing'):

        mock_transcribe.return_value = {
            'success': True,
            'transcription': 'Voice message transcription'
        }

        await handle_voice(update, context)

        # Verify transcription called
        mock_transcribe.assert_called_once()


@pytest.mark.asyncio
async def test_handle_voice_stores_transcription(test_db, mock_env):
    """Test that voice transcription is stored in database."""
    from bot_server import handle_voice
    from database import get_unprocessed_messages

    update = Mock()
    update.effective_chat.id = 123456789
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.message.message_id = 12345
    update.message.reply_text = AsyncMock()
    update.message.voice.get_file = AsyncMock()

    mock_file = Mock()
    mock_file.download_to_drive = AsyncMock()
    update.message.voice.get_file.return_value = mock_file

    context = Mock()

    with patch('bot_server.DB_PATH', test_db), \
         patch('bot_server.is_whitelisted', return_value=True), \
         patch('bot_server.transcribe_voice') as mock_transcribe, \
         patch('bot_server.trigger_processing'):

        mock_transcribe.return_value = {
            'success': True,
            'transcription': 'Stored transcription'
        }

        await handle_voice(update, context)

        # Verify transcription in database
        messages = get_unprocessed_messages(test_db)
        assert len(messages) == 1
        assert messages[0]['voice_transcription'] == 'Stored transcription'


@pytest.mark.asyncio
async def test_handle_voice_transcription_failure(test_db, mock_env):
    """Test handling of transcription failure."""
    from bot_server import handle_voice

    update = Mock()
    update.effective_chat.id = 123456789
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.message.message_id = 12345
    update.message.reply_text = AsyncMock()
    update.message.voice.get_file = AsyncMock()

    mock_file = Mock()
    mock_file.download_to_drive = AsyncMock()
    update.message.voice.get_file.return_value = mock_file

    context = Mock()

    with patch('bot_server.DB_PATH', test_db), \
         patch('bot_server.is_whitelisted', return_value=True), \
         patch('bot_server.transcribe_voice') as mock_transcribe, \
         patch('bot_server.trigger_processing'):

        mock_transcribe.return_value = {
            'success': False,
            'error': 'Transcription failed'
        }

        await handle_voice(update, context)

        # Should send error message to user
        update.message.reply_text.assert_called()
        call_args = str(update.message.reply_text.call_args)
        assert "transcription" in call_args.lower() or "error" in call_args.lower()


@pytest.mark.asyncio
async def test_trigger_processing_subprocess():
    """Test that trigger_processing spawns subprocess."""
    from bot_server import trigger_processing

    with patch('subprocess.Popen') as mock_popen:
        trigger_processing()

        # Verify subprocess called
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        # Should call telegram-process.sh
        assert any('telegram-process' in str(arg) for arg in call_args)
