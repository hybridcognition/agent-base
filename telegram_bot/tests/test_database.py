"""Tests for database.py - SQLite operations."""
import os
import sqlite3
from datetime import datetime

import pytest


def test_init_db_creates_tables(test_db):
    """Test that init_db creates both required tables."""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    # Check messages table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
    assert cursor.fetchone() is not None

    # Check processing_lock table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processing_lock'")
    assert cursor.fetchone() is not None

    conn.close()


def test_messages_table_schema(test_db):
    """Test that messages table has correct columns."""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(messages)")
    columns = {row[1] for row in cursor.fetchall()}

    expected_columns = {'id', 'chat_id', 'user_id', 'username', 'message_id',
                        'text', 'voice_file_path', 'voice_transcription',
                        'direction', 'processed', 'created_at'}

    assert expected_columns.issubset(columns)
    conn.close()


def test_processing_lock_singleton(test_db):
    """Test that processing_lock enforces singleton pattern."""
    from database import get_db_connection

    conn = get_db_connection(test_db)
    cursor = conn.cursor()

    # Verify row with id=1 already exists (from init_db)
    cursor.execute("SELECT COUNT(*) FROM processing_lock WHERE id = 1")
    assert cursor.fetchone()[0] == 1

    # Try to insert row with id=2 (should fail due to CHECK constraint)
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            "INSERT INTO processing_lock (id, is_locked) VALUES (2, 0)"
        )
        conn.commit()

    conn.close()


def test_add_incoming_message(test_db, sample_message):
    """Test adding incoming message to database."""
    from database import add_incoming_message

    message_id = add_incoming_message(
        test_db,
        sample_message["chat_id"],
        sample_message["user_id"],
        sample_message["username"],
        sample_message["message_id"],
        sample_message["text"]
    )

    assert message_id is not None

    # Verify message in database
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
    row = cursor.fetchone()

    assert row is not None
    assert row[1] == sample_message["chat_id"]  # chat_id
    assert row[5] == sample_message["text"]      # text
    assert row[8] == "incoming"                  # direction
    assert row[9] == 0                           # processed = False

    conn.close()


def test_add_outgoing_message(test_db):
    """Test adding outgoing message to database."""
    from database import add_outgoing_message

    chat_id = 123456789
    text = "Response message"

    message_id = add_outgoing_message(test_db, chat_id, text)
    assert message_id is not None

    # Verify message in database
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
    row = cursor.fetchone()

    assert row is not None
    assert row[1] == chat_id                # chat_id
    assert row[5] == text                   # text
    assert row[8] == "outgoing"             # direction

    conn.close()


def test_add_voice_message(test_db, sample_voice_message):
    """Test adding voice message with transcription."""
    from database import add_incoming_message

    message_id = add_incoming_message(
        test_db,
        sample_voice_message["chat_id"],
        sample_voice_message["user_id"],
        sample_voice_message["username"],
        sample_voice_message["message_id"],
        None,  # No text for voice message
        sample_voice_message["voice_file_path"],
        sample_voice_message["voice_transcription"]
    )

    assert message_id is not None

    # Verify voice data stored
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT voice_file_path, voice_transcription FROM messages WHERE id = ?",
                   (message_id,))
    row = cursor.fetchone()

    assert row[0] == sample_voice_message["voice_file_path"]
    assert row[1] == sample_voice_message["voice_transcription"]

    conn.close()


def test_get_unprocessed_messages_empty(test_db):
    """Test getting unprocessed messages when none exist."""
    from database import get_unprocessed_messages

    messages = get_unprocessed_messages(test_db)
    assert messages == []


def test_get_unprocessed_messages(test_db):
    """Test getting unprocessed incoming messages."""
    from database import add_incoming_message, get_unprocessed_messages

    # Add processed message (should not be returned)
    add_incoming_message(test_db, 111, 111, "user1", 1, "Processed message")
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET processed = 1 WHERE chat_id = 111")
    conn.commit()
    conn.close()

    # Add unprocessed messages
    add_incoming_message(test_db, 222, 222, "user2", 2, "Unprocessed 1")
    add_incoming_message(test_db, 333, 333, "user3", 3, "Unprocessed 2")

    # Add outgoing message (should not be returned)
    from database import add_outgoing_message
    add_outgoing_message(test_db, 444, "Outgoing message")

    messages = get_unprocessed_messages(test_db)

    assert len(messages) == 2
    assert messages[0]['text'] == "Unprocessed 1"
    assert messages[1]['text'] == "Unprocessed 2"


def test_mark_messages_processed(test_db):
    """Test marking messages as processed."""
    from database import add_incoming_message, mark_messages_processed, get_unprocessed_messages

    # Add messages
    id1 = add_incoming_message(test_db, 111, 111, "user1", 1, "Message 1")
    id2 = add_incoming_message(test_db, 222, 222, "user2", 2, "Message 2")

    # Verify unprocessed
    messages = get_unprocessed_messages(test_db)
    assert len(messages) == 2

    # Mark as processed
    mark_messages_processed(test_db, [id1, id2])

    # Verify processed
    messages = get_unprocessed_messages(test_db)
    assert len(messages) == 0


def test_acquire_lock_success(test_db):
    """Test acquiring lock when unlocked."""
    from database import acquire_lock

    result = acquire_lock(test_db)
    assert result is True

    # Verify lock state in database
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT is_locked FROM processing_lock WHERE id = 1")
    row = cursor.fetchone()
    assert row[0] == 1  # is_locked = True
    conn.close()


def test_acquire_lock_already_locked(test_db):
    """Test acquiring lock when already locked."""
    from database import acquire_lock

    # Acquire lock first time
    assert acquire_lock(test_db) is True

    # Try to acquire again (should fail)
    assert acquire_lock(test_db) is False


def test_release_lock(test_db):
    """Test releasing lock."""
    from database import acquire_lock, release_lock, is_locked

    # Acquire lock
    acquire_lock(test_db)
    assert is_locked(test_db) is True

    # Release lock
    release_lock(test_db)
    assert is_locked(test_db) is False


def test_is_locked(test_db):
    """Test checking lock status."""
    from database import is_locked, acquire_lock, release_lock

    # Initially unlocked
    assert is_locked(test_db) is False

    # Acquire lock
    acquire_lock(test_db)
    assert is_locked(test_db) is True

    # Release lock
    release_lock(test_db)
    assert is_locked(test_db) is False


def test_message_ordering(test_db):
    """Test that messages are returned in creation order."""
    from database import add_incoming_message, get_unprocessed_messages

    # Add messages with slight delays to ensure different timestamps
    add_incoming_message(test_db, 111, 111, "user1", 1, "First")
    add_incoming_message(test_db, 222, 222, "user2", 2, "Second")
    add_incoming_message(test_db, 333, 333, "user3", 3, "Third")

    messages = get_unprocessed_messages(test_db)

    assert len(messages) == 3
    assert messages[0]['text'] == "First"
    assert messages[1]['text'] == "Second"
    assert messages[2]['text'] == "Third"


def test_lock_timestamp(test_db):
    """Test that lock timestamp is set correctly."""
    from database import acquire_lock, get_db_connection

    before = datetime.utcnow()
    acquire_lock(test_db)
    after = datetime.utcnow()

    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT locked_at FROM processing_lock WHERE id = 1")
    row = cursor.fetchone()

    # locked_at should be between before and after
    locked_at = datetime.fromisoformat(row[0])
    assert before <= locked_at <= after

    conn.close()


def test_concurrent_message_handling(test_db):
    """Test handling multiple unprocessed messages correctly."""
    from database import add_incoming_message, get_unprocessed_messages, mark_messages_processed

    # Add multiple messages
    ids = []
    for i in range(5):
        msg_id = add_incoming_message(test_db, 100 + i, 100 + i, f"user{i}", i, f"Message {i}")
        ids.append(msg_id)

    # Get all unprocessed
    messages = get_unprocessed_messages(test_db)
    assert len(messages) == 5

    # Mark first 3 as processed
    mark_messages_processed(test_db, ids[:3])

    # Get remaining unprocessed
    messages = get_unprocessed_messages(test_db)
    assert len(messages) == 2
    assert messages[0]['text'] == "Message 3"
    assert messages[1]['text'] == "Message 4"


def test_message_lifecycle_workflow(test_db):
    """Test complete message lifecycle from incoming to processed to response."""
    from database import (add_incoming_message, get_unprocessed_messages,
                          mark_messages_processed, add_outgoing_message)

    # Incoming message
    msg_id = add_incoming_message(test_db, 123, 123, "user", 1, "Hello agent")

    # Get unprocessed
    messages = get_unprocessed_messages(test_db)
    assert len(messages) == 1
    assert messages[0]['text'] == "Hello agent"

    # Process and respond
    add_outgoing_message(test_db, 123, "Hello user")

    # Mark as processed
    mark_messages_processed(test_db, [msg_id])

    # Verify no unprocessed remain
    messages = get_unprocessed_messages(test_db)
    assert len(messages) == 0

    # Verify outgoing message stored
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM messages WHERE direction = 'outgoing'")
    row = cursor.fetchone()
    assert row[0] == "Hello user"
    conn.close()


def test_add_outgoing_message_creates_correct_record(test_db):
    """Test that outgoing messages are stored with correct direction."""
    from database import add_outgoing_message, get_db_connection

    chat_id = 123456789
    text = "Outgoing test message"

    msg_id = add_outgoing_message(test_db, chat_id, text)

    # Verify message stored correctly
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT direction, text, chat_id FROM messages WHERE id = ?",
        (msg_id,)
    )
    row = cursor.fetchone()

    assert row is not None
    assert row[0] == "outgoing"
    assert row[1] == text
    assert row[2] == chat_id
    conn.close()


def test_release_lock_when_not_locked(test_db):
    """Test releasing lock when it's not currently held."""
    from database import release_lock, is_locked

    # Lock should start as unlocked
    assert is_locked(test_db) is False

    # Releasing unlocked lock should not raise error
    release_lock(test_db)

    # Should still be unlocked
    assert is_locked(test_db) is False
