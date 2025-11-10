"""Shared pytest fixtures for all tests."""
import os
import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def test_db(tmp_path):
    """Provide temporary SQLite database for testing.

    Creates a real SQLite database with full schema.
    Automatically cleaned up after test completes.
    """
    db_path = tmp_path / "test_messages.db"

    # Import here to avoid circular dependencies
    from database import init_db
    init_db(str(db_path))

    yield str(db_path)
    # tmp_path automatically cleaned by pytest


@pytest.fixture
def sample_audio_file():
    """Provide path to sample OGG voice file for transcription tests."""
    return str(Path(__file__).parent / "fixtures" / "sample_voice.ogg")


@pytest.fixture
def sample_message():
    """Provide standard message data structure for testing."""
    return {
        "chat_id": 123456789,
        "user_id": 123456789,
        "username": "testuser",
        "message_id": 12345,
        "text": "Test message",
        "direction": "incoming"
    }


@pytest.fixture
def sample_voice_message():
    """Provide voice message data structure for testing."""
    return {
        "chat_id": 123456789,
        "user_id": 123456789,
        "username": "testuser",
        "message_id": 67890,
        "voice_file_path": "/tmp/test_voice.ogg",
        "voice_transcription": "This is a test voice message",
        "direction": "incoming"
    }


@pytest.fixture
def mock_env(monkeypatch):
    """Provide mock environment variables for testing."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
    monkeypatch.setenv("ALLOWED_CHAT_IDS", "123456789,987654321")
    monkeypatch.setenv("WORKSPACE_DIR", "/root/workspace")
    monkeypatch.setenv("REPO_NAME", "test-repo")
